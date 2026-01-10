from django.shortcuts import render

# trucking/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Sum, Count
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import pyotp
import qrcode
import io
import base64

from django.utils import timezone

from .models import Driver, Truck, Trip, RoutePoint, Document, Payroll, TripUpdate
from .serializers import (
    DriverSerializer, DriverCreateSerializer, TruckSerializer,
    TripSerializer, TripCreateSerializer, RoutePointSerializer,
    DocumentSerializer, PayrollSerializer, TripUpdateSerializer,
    DriverMileageSerializer, OTPSetupSerializer, OTPVerifySerializer,
    PasskeyRegistrationSerializer, AssignTruckSerializer, AssignTripSerializer
)
from .permissions import IsAdmin, IsAdminOrDriver, IsOwnerOrAdmin

User = get_user_model()


class DriverViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Driver management
    Admin can perform all operations
    Drivers can only view their own profile
    """
    queryset = Driver.objects.all().select_related('user', 'current_truck')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DriverCreateSerializer
        return DriverSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            # Drivers can only see themselves
            return Driver.objects.filter(user=user)
        # Admin and staff can see all
        return Driver.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current driver's profile"""
        try:
            driver = request.user.driver_profile
            serializer = self.get_serializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def mileage(self, request, pk=None):
        """Get driver's mileage per trip"""
        driver = self.get_object()
        trips = Trip.objects.filter(
            driver=driver,
            status='DELIVERED',
            actual_miles__isnull=False
        ).values(
            'id', 'trip_number', 'actual_miles',
            'origin_city', 'destination_city',
            'actual_delivery'
        )
        
        mileage_data = [
            {
                'trip_id': t['id'],
                'trip_number': t['trip_number'],
                'actual_miles': t['actual_miles'],
                'origin': t['origin_city'],
                'destination': t['destination_city'],
                'completed_date': t['actual_delivery']
            }
            for t in trips
        ]
        
        serializer = DriverMileageSerializer(mileage_data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def assign_truck(self, request, pk=None):
        """Assign a truck to a driver"""
        driver = self.get_object()
        serializer = AssignTruckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        truck = Truck.objects.get(id=serializer.validated_data['truck_id'])
        
        # Unassign previous driver if any
        if hasattr(truck, 'current_driver') and truck.current_driver:
            truck.current_driver.current_truck = None
            truck.current_driver.save()
        
        driver.current_truck = truck
        driver.save()
        
        truck.status = 'IN_USE'
        truck.save()
        
        return Response({
            'message': f'Truck {truck.truck_number} assigned to {driver.user.get_full_name()}',
            'driver': DriverSerializer(driver).data
        })
    
    @action(detail=True, methods=['get'])
    def payroll(self, request, pk=None):
        """Get driver's payroll records"""
        driver = self.get_object()
        
        # Check permissions - drivers can only see their own
        if request.user.role == 'DRIVER' and driver.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        payroll_records = Payroll.objects.filter(driver=driver)
        serializer = PayrollSerializer(payroll_records, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get driver's documents"""
        driver = self.get_object()
        
        # Check permissions
        if request.user.role == 'DRIVER' and driver.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        documents = Document.objects.filter(driver=driver)
        doc_type = request.query_params.get('type')
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        
        serializer = DocumentSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)


class TruckViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Truck management
    Only admin can access
    """
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        queryset = Truck.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available trucks"""
        trucks = Truck.objects.filter(status='AVAILABLE')
        serializer = self.get_serializer(trucks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        """Mark truck for maintenance"""
        truck = self.get_object()
        truck.status = 'MAINTENANCE'
        truck.last_maintenance = datetime.now().date()
        
        next_maintenance = request.data.get('next_maintenance_due')
        if next_maintenance:
            truck.next_maintenance_due = next_maintenance
        
        truck.save()
        
        serializer = self.get_serializer(truck)
        return Response(serializer.data)


class TripViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Trip management
    Admin can perform all operations
    Drivers can view and update their assigned trips
    """
    queryset = Trip.objects.all().select_related('driver__user', 'truck')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TripCreateSerializer
        return TripSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Trip.objects.all()
        
        if user.role == 'DRIVER':
            # Drivers only see their own trips
            queryset = queryset.filter(driver__user=user)
        
        # Filters
        broker = self.request.query_params.get('broker')
        status_filter = self.request.query_params.get('status')
        driver_id = self.request.query_params.get('driver_id')
        
        if broker:
            queryset = queryset.filter(broker__icontains=broker)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if driver_id and user.role != 'DRIVER':
            queryset = queryset.filter(driver_id=driver_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_trips(self, request):
        """Get current driver's trips"""
        if not hasattr(request.user, 'driver_profile'):
            return Response({'error': 'User is not a driver'}, status=status.HTTP_400_BAD_REQUEST)
        
        trips = Trip.objects.filter(driver=request.user.driver_profile)
        serializer = self.get_serializer(trips, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current_trip(self, request):
        """Get driver's current active trip"""
        if not hasattr(request.user, 'driver_profile'):
            return Response({'error': 'User is not a driver'}, status=status.HTTP_400_BAD_REQUEST)
        
        trip = Trip.objects.filter(
            driver=request.user.driver_profile,
            status__in=['ASSIGNED', 'IN_TRANSIT']
        ).first()
        
        if trip:
            serializer = self.get_serializer(trip)
            return Response(serializer.data)
        return Response({'current_trip': None})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update trip status with notes"""
        trip = self.get_object()
        
        # Check permissions - drivers can only update their own trips
        if request.user.role == 'DRIVER' and trip.driver.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        location = request.data.get('location', '')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update trip status
        trip.status = new_status
        
        # Update timestamps based on status
        if new_status == 'IN_TRANSIT' and not trip.actual_pickup:
            trip.actual_pickup = datetime.now()
        elif new_status == 'DELIVERED' and not trip.actual_delivery:
            trip.actual_delivery = datetime.now()
            
            # Update driver's total miles if actual miles recorded
            if trip.actual_miles:
                trip.driver.total_miles += trip.actual_miles
                trip.driver.save()
            
            # Make truck available again
            trip.truck.status = 'AVAILABLE'
            trip.truck.save()
        
        trip.save()
        
        # Create trip update record
        TripUpdate.objects.create(
            trip=trip,
            updated_by=request.user,
            status=new_status,
            notes=notes,
            location=location,
            latitude=latitude,
            longitude=longitude
        )
        
        serializer = self.get_serializer(trip)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_route_point(self, request, pk=None):
        """Add GPS tracking point to trip route"""
        trip = self.get_object()
        
        # Only driver assigned to trip can add route points
        if request.user.role == 'DRIVER' and trip.driver.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoutePointSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(trip=trip)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def route(self, request, pk=None):
        """Get trip's route points"""
        trip = self.get_object()
        route_points = trip.route_points.all()
        serializer = RoutePointSerializer(route_points, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        """Get trip's status updates"""
        trip = self.get_object()
        updates = trip.updates.all()
        serializer = TripUpdateSerializer(updates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def assign(self, request, pk=None):
        """Assign trip to driver and truck"""
        trip = self.get_object()
        serializer = AssignTripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        driver = Driver.objects.get(id=serializer.validated_data['driver_id'])
        truck = Truck.objects.get(id=serializer.validated_data['truck_id'])
        
        trip.driver = driver
        trip.truck = truck
        trip.status = 'ASSIGNED'
        trip.save()
        
        # Update truck status
        truck.status = 'IN_USE'
        truck.save()
        
        # Update driver's current truck
        driver.current_truck = truck
        driver.save()
        
        return Response(TripSerializer(trip).data)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document management
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Document.objects.all()
        
        if user.role == 'DRIVER':
            # Drivers only see their own documents
            queryset = queryset.filter(driver__user=user)
        
        # Filters
        driver_id = self.request.query_params.get('driver_id')
        trip_id = self.request.query_params.get('trip_id')
        doc_type = self.request.query_params.get('type')
        
        if driver_id and user.role != 'DRIVER':
            queryset = queryset.filter(driver_id=driver_id)
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        return queryset
    
    def perform_create(self, serializer):
        # Set file metadata
        file_obj = self.request.FILES.get('file')
        serializer.save(
            uploaded_by=self.request.user,
            file_name=file_obj.name,
            file_size=file_obj.size
        )


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payroll management
    Only admin can create/update
    Drivers can view their own
    """
    queryset = Payroll.objects.all().select_related('driver__user')
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Payroll.objects.all()
        
        if user.role == 'DRIVER':
            # Drivers only see their own payroll
            queryset = queryset.filter(driver__user=user)
        
        driver_id = self.request.query_params.get('driver_id')
        if driver_id and user.role != 'DRIVER':
            queryset = queryset.filter(driver_id=driver_id)
        
        return queryset





# Admin Site Callbacks and Custom Views
def dashboard_callback(request, context):
    now = timezone.now()
    today = now.date()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    context.update({
        'stats': {
            'total_drivers': Driver.objects.count(),
            'active_drivers': Driver.objects.filter(status='ACTIVE').count(),
            'active_trips': Trip.objects.filter(
                status__in=['ASSIGNED', 'IN_TRANSIT']
            ).count(),
            'in_transit': Trip.objects.filter(status='IN_TRANSIT').count(),
            'total_trucks': Truck.objects.count(),
            'available_trucks': Truck.objects.filter(status='AVAILABLE').count(),
            'in_use_trucks': Truck.objects.filter(status='IN_USE').count(),
            'maintenance_trucks': Truck.objects.filter(status='MAINTENANCE').count(),
            'available_trucks_percent': round(
                (Truck.objects.filter(status='AVAILABLE').count() /
                 max(Truck.objects.count(), 1)) * 100, 1
            ),
            'monthly_revenue': Trip.objects.filter(
                status='DELIVERED',
                actual_delivery__gte=thirty_days_ago
            ).aggregate(total=Sum('rate'))['total'] or 0,
        },
        'recent_trips': Trip.objects.select_related(
            'driver__user', 'truck'
        ).order_by('-created_at')[:5],
        'top_drivers': Driver.objects.annotate(
            completed_trips=Count(
                'trips',
                filter=Q(
                    trips__status='DELIVERED',
                    trips__actual_delivery__gte=thirty_days_ago
                )
            )
        ).filter(completed_trips__gt=0).order_by('-completed_trips')[:5],
    })

    return context



def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Production", "danger"] # info, danger, warning, success


def badge_callback(request):
    return 3

def permission_callback(request):
    return request.user.has_perm("sample_app.change_model")
