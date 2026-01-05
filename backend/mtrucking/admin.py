
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Driver, Truck, Trip, RoutePoint, Document, Payroll, TripUpdate

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'otp_enabled')}),
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'status', 'current_truck', 'total_miles']
    list_filter = ['status']
    search_fields = ['license_number', 'user__username', 'user__email']

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['truck_number', 'make', 'model', 'year', 'status', 'mileage']
    list_filter = ['status', 'make']
    search_fields = ['truck_number', 'vin', 'license_plate']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_number', 'driver', 'truck', 'status', 'scheduled_pickup', 'scheduled_delivery']
    list_filter = ['status', 'broker']
    search_fields = ['trip_number', 'load_number', 'broker']
    date_hierarchy = 'scheduled_pickup'

admin.site.register(RoutePoint)
admin.site.register(Document)
admin.site.register(Payroll)
admin.site.register(TripUpdate)
