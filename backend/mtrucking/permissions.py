# trucking/permissions.py
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Only admin users can access"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAdminOrDriver(permissions.BasePermission):
    """Admin or driver can access"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'DRIVER']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Object owner or admin can access"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'driver'):
            return obj.driver.user == request.user
        
        return False









