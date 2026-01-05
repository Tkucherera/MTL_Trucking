# trucking/authentication.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
import pyotp
import qrcode
import io
import base64
import secrets

User = get_user_model()


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def login_username_password(request):
    """
    Standard username/password authentication
    POST /api/auth/login/
    Body: {"username": "user", "password": "pass"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if OTP is enabled
    if user.otp_enabled:
        # Create temporary session token
        temp_token = secrets.token_urlsafe(32)
        # Store in cache or database (simplified here)
        request.session['otp_user_id'] = user.id
        request.session['otp_temp_token'] = temp_token
        
        return Response({
            'requires_otp': True,
            'temp_token': temp_token,
            'message': 'Please provide OTP code'
        })
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        'tokens': tokens,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_login(request):
    """
    Verify OTP and complete login
    POST /api/auth/login/otp/
    Body: {"temp_token": "...", "otp_code": "123456"}
    """
    temp_token = request.data.get('temp_token')
    otp_code = request.data.get('otp_code')
    
    if not temp_token or not otp_code:
        return Response(
            {'error': 'Temp token and OTP code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify temp token (simplified - should use cache/db)
    user_id = request.session.get('otp_user_id')
    stored_token = request.session.get('otp_temp_token')
    
    if not user_id or stored_token != temp_token:
        return Response(
            {'error': 'Invalid or expired temp token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify OTP
    totp = pyotp.TOTP(user.otp_secret)
    if not totp.verify(otp_code, valid_window=1):
        return Response(
            {'error': 'Invalid OTP code'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Clear session
    del request.session['otp_user_id']
    del request.session['otp_temp_token']
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        'tokens': tokens,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_otp(request):
    """
    Setup OTP/2FA for user
    POST /api/auth/otp/setup/
    Returns QR code and secret
    """
    user = request.user
    
    if user.otp_enabled:
        return Response(
            {'error': 'OTP is already enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate secret
    secret = pyotp.random_base32()
    user.otp_secret = secret
    user.save()
    
    # Generate provisioning URI
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name='Trucking Company'
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return Response({
        'secret': secret,
        'qr_code': f'data:image/png;base64,{qr_code_base64}',
        'provisioning_uri': provisioning_uri
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp_setup(request):
    """
    Verify OTP setup and enable 2FA
    POST /api/auth/otp/verify/
    Body: {"otp_code": "123456"}
    """
    user = request.user
    otp_code = request.data.get('otp_code')
    
    if not otp_code:
        return Response(
            {'error': 'OTP code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.otp_secret:
        return Response(
            {'error': 'OTP not set up. Please call /setup/ first'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    totp = pyotp.TOTP(user.otp_secret)
    if not totp.verify(otp_code, valid_window=1):
        return Response(
            {'error': 'Invalid OTP code'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user.otp_enabled = True
    user.save()
    
    return Response({
        'message': 'OTP successfully enabled',
        'otp_enabled': True
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_otp(request):
    """
    Disable OTP/2FA for user
    POST /api/auth/otp/disable/
    Body: {"password": "user_password"}
    """
    user = request.user
    password = request.data.get('password')
    
    if not password:
        return Response(
            {'error': 'Password is required to disable OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.check_password(password):
        return Response(
            {'error': 'Invalid password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user.otp_enabled = False
    user.otp_secret = None
    user.save()
    
    return Response({
        'message': 'OTP successfully disabled',
        'otp_enabled': False
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp_email(request):
    """
    Request OTP via email (alternative to authenticator app)
    POST /api/auth/otp/email/
    Body: {"email": "user@example.com"}
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal if email exists
        return Response({'message': 'If the email exists, an OTP has been sent'})
    
    # Generate 6-digit OTP
    otp_code = secrets.randbelow(1000000)
    otp_code_str = f'{otp_code:06d}'
    
    # Store in cache/session (expires in 5 minutes)
    request.session[f'email_otp_{email}'] = otp_code_str
    request.session.set_expiry(300)  # 5 minutes
    
    # Send email
    send_mail(
        'Your Login OTP',
        f'Your OTP code is: {otp_code_str}\n\nThis code expires in 5 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
    return Response({'message': 'OTP sent to email'})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_email(request):
    """
    Verify email OTP and login
    POST /api/auth/otp/email/verify/
    Body: {"email": "user@example.com", "otp_code": "123456"}
    """
    email = request.data.get('email')
    otp_code = request.data.get('otp_code')
    
    if not email or not otp_code:
        return Response(
            {'error': 'Email and OTP code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stored_otp = request.session.get(f'email_otp_{email}')
    
    if not stored_otp or stored_otp != otp_code:
        return Response(
            {'error': 'Invalid or expired OTP code'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Clear OTP from session
    del request.session[f'email_otp_{email}']
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        'tokens': tokens,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_passkey(request):
    """
    Register passkey/WebAuthn credential
    POST /api/auth/passkey/register/
    Body: {"credential_id": "...", "public_key": "..."}
    """
    user = request.user
    credential_id = request.data.get('credential_id')
    public_key = request.data.get('public_key')
    
    if not credential_id or not public_key:
        return Response(
            {'error': 'Credential ID and public key are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.passkey_credential_id = credential_id
    user.passkey_public_key = public_key
    user.save()
    
    return Response({
        'message': 'Passkey successfully registered',
        'credential_id': credential_id
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_passkey(request):
    """
    Login using passkey
    POST /api/auth/passkey/login/
    Body: {"credential_id": "...", "signature": "..."}
    
    Note: This is a simplified implementation.
    Production should use proper WebAuthn library with challenge verification
    """
    credential_id = request.data.get('credential_id')
    signature = request.data.get('signature')
    
    if not credential_id or not signature:
        return Response(
            {'error': 'Credential ID and signature are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(passkey_credential_id=credential_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # TODO: Verify signature using public key
    # This is where you'd verify the WebAuthn signature
    # For now, we'll assume it's valid if credential_id matches
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        'tokens': tokens,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user (blacklist refresh token)
    POST /api/auth/logout/
    Body: {"refresh": "refresh_token"}
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except Exception:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Refresh access token
    POST /api/auth/refresh/
    Body: {"refresh": "refresh_token"}
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token)
        })
    except Exception:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )