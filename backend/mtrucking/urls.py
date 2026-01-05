from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from . import authentication

router = DefaultRouter()
router.register(r'drivers', views.DriverViewSet, basename='driver')
router.register(r'trucks', views.TruckViewSet, basename='truck')
router.register(r'trips', views.TripViewSet, basename='trip')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'payroll', views.PayrollViewSet, basename='payroll')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', authentication.login_username_password, name='login'),
    path('auth/login/otp/', authentication.verify_otp_login, name='verify-otp-login'),
    path('auth/logout/', authentication.logout, name='logout'),
    path('auth/refresh/', authentication.refresh_token, name='refresh-token'),
    
    # OTP/2FA setup
    path('auth/otp/setup/', authentication.setup_otp, name='setup-otp'),
    path('auth/otp/verify/', authentication.verify_otp_setup, name='verify-otp'),
    path('auth/otp/disable/', authentication.disable_otp, name='disable-otp'),
    
    # Email OTP
    path('auth/otp/email/', authentication.request_otp_email, name='request-otp-email'),
    path('auth/otp/email/verify/', authentication.verify_otp_email, name='verify-otp-email'),
    
    # Passkey authentication
    path('auth/passkey/register/', authentication.register_passkey, name='register-passkey'),
    path('auth/passkey/login/', authentication.login_passkey, name='login-passkey'),
    
    # ViewSet routes
    path('', include(router.urls)),
]
