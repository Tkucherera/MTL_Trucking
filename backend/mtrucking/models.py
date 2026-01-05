# trucking/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class User(AbstractUser):
    """Extended user model with role-based access"""
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('DRIVER', 'Driver'),
        ('STAFF', 'Staff'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='DRIVER')
    phone = models.CharField(max_length=15, blank=True)
    # For passkey authentication
    passkey_credential_id = models.CharField(max_length=255, blank=True, null=True)
    passkey_public_key = models.TextField(blank=True, null=True)
    # For OTP authentication
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    otp_enabled = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'


class Driver(models.Model):
    """Driver profile extending User"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ON_LEAVE', 'On Leave'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    cdl_class = models.CharField(max_length=10)  # A, B, C
    cdl_expiry = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    hire_date = models.DateField(auto_now_add=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    current_truck = models.ForeignKey('Truck', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_driver')
    total_miles = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'drivers'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['license_number']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"


class Truck(models.Model):
    """Truck/Vehicle information"""
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('IN_USE', 'In Use'),
        ('MAINTENANCE', 'Maintenance'),
        ('OUT_OF_SERVICE', 'Out of Service'),
    ]
    
    truck_number = models.CharField(max_length=50, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    vin = models.CharField(max_length=17, unique=True)
    license_plate = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    mileage = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance_due = models.DateField(null=True, blank=True)
    gps_device_id = models.CharField(max_length=100, blank=True, null=True)  # For future GPS tracking
    fuel_capacity = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'trucks'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['truck_number']),
        ]
    
    def __str__(self):
        return f"{self.truck_number} - {self.make} {self.model}"


class Trip(models.Model):
    """Trip/Load information"""
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    trip_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='trips')
    truck = models.ForeignKey(Truck, on_delete=models.PROTECT, related_name='trips')
    broker = models.CharField(max_length=100)
    load_number = models.CharField(max_length=50, blank=True)
    
    # Origin and Destination
    origin_address = models.TextField()
    origin_city = models.CharField(max_length=100)
    origin_state = models.CharField(max_length=2)
    origin_zip = models.CharField(max_length=10)
    origin_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    origin_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    destination_address = models.TextField()
    destination_city = models.CharField(max_length=100)
    destination_state = models.CharField(max_length=2)
    destination_zip = models.CharField(max_length=10)
    destination_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    destination_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Trip Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    scheduled_pickup = models.DateTimeField()
    scheduled_delivery = models.DateTimeField()
    actual_pickup = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    
    # Financial
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    driver_pay = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Mileage tracking
    estimated_miles = models.DecimalField(max_digits=8, decimal_places=2)
    actual_miles = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Cargo details
    cargo_description = models.TextField(blank=True)
    cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trips'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['trip_number']),
        ]
    
    def __str__(self):
        return f"{self.trip_number} - {self.driver.user.get_full_name()}"


class RoutePoint(models.Model):
    """GPS tracking points for trips"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='route_points')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # mph
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # degrees
    
    class Meta:
        db_table = 'route_points'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['trip', 'timestamp']),
        ]


class Document(models.Model):
    """File storage for various documents"""
    DOC_TYPE_CHOICES = [
        ('LICENSE', 'License'),
        ('CDL', 'CDL'),
        ('INSURANCE', 'Insurance'),
        ('PAYSLIP', 'Payslip'),
        ('BOL', 'Bill of Lading'),
        ('POD', 'Proof of Delivery'),
        ('INSPECTION', 'Inspection Report'),
        ('OTHER', 'Other'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    
    document_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()  # bytes
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']


class Payroll(models.Model):
    """Payroll records for drivers"""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='payroll_records')
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    
    # Earnings breakdown
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mileage_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    
    miles_driven = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trips_completed = models.IntegerField(default=0)
    
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    
    payslip = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='payroll_record')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payroll'
        ordering = ['-pay_period_end']
        unique_together = ['driver', 'pay_period_start', 'pay_period_end']


class TripUpdate(models.Model):
    """Status updates and notes for trips"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trip_updates'
        ordering = ['-timestamp']