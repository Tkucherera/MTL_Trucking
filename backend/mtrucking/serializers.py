# trucking/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Driver, Truck, Trip, RoutePoint, Document, Payroll, TripUpdate
import pyotp

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'otp_enabled']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'role']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    current_truck_number = serializers.CharField(source='current_truck.truck_number', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = '__all__'
        read_only_fields = ['total_miles']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class DriverCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    
    class Meta:
        model = Driver
        fields = '__all__'
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'DRIVER'
        user = User.objects.create_user(**user_data)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver


class TruckSerializer(serializers.ModelSerializer):
    current_driver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Truck
        fields = '__all__'
    
    def get_current_driver_name(self, obj):
        if hasattr(obj, 'current_driver') and obj.current_driver:
            return obj.current_driver.user.get_full_name()
        return None


class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = '__all__'
        read_only_fields = ['timestamp']


class TripUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = TripUpdate
        fields = '__all__'
        read_only_fields = ['timestamp', 'updated_by']


class TripSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    truck_number = serializers.CharField(source='truck.truck_number', read_only=True)
    recent_updates = TripUpdateSerializer(many=True, read_only=True, source='updates')
    route_points_count = serializers.IntegerField(source='route_points.count', read_only=True)
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['trip_number', 'created_at', 'updated_at']


class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['trip_number', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Ensure driver is active
        if data['driver'].status != 'ACTIVE':
            raise serializers.ValidationError("Cannot assign trip to inactive driver")
        
        # Ensure truck is available
        if data['truck'].status not in ['AVAILABLE', 'IN_USE']:
            raise serializers.ValidationError("Truck is not available")
        
        return data
    
    def create(self, validated_data):
        trip = super().create(validated_data)
        # Update truck status
        trip.truck.status = 'IN_USE'
        trip.truck.save()
        # Update driver's current truck
        trip.driver.current_truck = trip.truck
        trip.driver.save()
        return trip


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'uploaded_by', 'file_size']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class PayrollSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    payslip_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_payslip_url(self, obj):
        if obj.payslip and obj.payslip.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.payslip.file.url)
        return None


class DriverMileageSerializer(serializers.Serializer):
    """Serializer for tracking driver miles per trip"""
    trip_id = serializers.IntegerField()
    trip_number = serializers.CharField()
    actual_miles = serializers.DecimalField(max_digits=8, decimal_places=2)
    origin = serializers.CharField()
    destination = serializers.CharField()
    completed_date = serializers.DateTimeField()


class OTPSetupSerializer(serializers.Serializer):
    """Serializer for OTP setup"""
    secret = serializers.CharField(read_only=True)
    qr_code = serializers.CharField(read_only=True)


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    token = serializers.CharField(max_length=6, min_length=6)


class PasskeyRegistrationSerializer(serializers.Serializer):
    """Serializer for passkey registration"""
    credential_id = serializers.CharField()
    public_key = serializers.CharField()


class AssignTruckSerializer(serializers.Serializer):
    """Serializer for assigning truck to driver"""
    truck_id = serializers.IntegerField()
    
    def validate_truck_id(self, value):
        try:
            truck = Truck.objects.get(id=value)
            if truck.status not in ['AVAILABLE', 'IN_USE']:
                raise serializers.ValidationError("Truck is not available")
        except Truck.DoesNotExist:
            raise serializers.ValidationError("Truck not found")
        return value


class AssignTripSerializer(serializers.Serializer):
    """Serializer for assigning trip to driver"""
    driver_id = serializers.IntegerField()
    truck_id = serializers.IntegerField()
    
    def validate(self, data):
        try:
            driver = Driver.objects.get(id=data['driver_id'])
            if driver.status != 'ACTIVE':
                raise serializers.ValidationError("Driver is not active")
        except Driver.DoesNotExist:
            raise serializers.ValidationError("Driver not found")
        
        try:
            truck = Truck.objects.get(id=data['truck_id'])
            if truck.status not in ['AVAILABLE', 'IN_USE']:
                raise serializers.ValidationError("Truck is not available")
        except Truck.DoesNotExist:
            raise serializers.ValidationError("Truck not found")
        
        return data