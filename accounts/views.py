"""
Authentication and user management views - Complete.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from datetime import timedelta
from django.db.models import Q

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import User
from accounts.serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    LoginSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, Enable2FASerializer,
    Verify2FASerializer, Login2FASerializer, RoleAssignSerializer
)
from accounts.permissions import IsAdmin, IsOwnerOrAdmin
from core.utils import (
    StandardResponse, generate_reset_token, generate_qr_code,
    send_email_notification, create_password_reset_link,
    verify_otp, get_client_ip, get_user_agent
)
from core.exceptions import (
    InvalidCredentialsError, InvalidTokenError, InvalidOTPError
)
from core.models import AuditLog

bearer_security = [{'Bearer': []}]
class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication operations.
    """
    
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def get_tokens_for_user(self, user):
        """Generate JWT tokens for user."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate user using username/email and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response('Login successful'),
            202: openapi.Response('2FA required'),
            400: 'Invalid credentials'
        }
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """User login endpoint."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        if user.is_2fa_enabled:
            temp_token = generate_reset_token()
            user.password_reset_token = temp_token
            user.password_reset_expires = timezone.now() + timedelta(minutes=5)
            user.save()
            
            return Response(
                StandardResponse.requires_2fa(temp_token),
                status=status.HTTP_202_ACCEPTED
            )
        
        tokens = self.get_tokens_for_user(user)
        user.last_login = timezone.now()
        user.save()
        
        AuditLog.objects.create(
            user=user,
            action='LOGIN',
            model_name='User',
            object_id=user.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return Response(
            StandardResponse.success(
                data={
                    'access_token': tokens['access'],
                    'refresh_token': tokens['refresh'],
                    'token_type': 'Bearer',
                    'expires_in': 3600,
                    'user': UserSerializer(user).data,
                    'requires_2fa': False
                }
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Verify Login 2FA",
        operation_description="Verify OTP code after login when 2FA is enabled",
        request_body=Login2FASerializer,
        responses={200: 'JWT Tokens issued'}
    )
    @action(detail=False, methods=['post'], url_path='verify-2fa')
    def verify_2fa(self, request):
        serializer = Login2FASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        temp_token = serializer.validated_data['temp_token']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.get(
                password_reset_token=temp_token,
                password_reset_expires__gt=timezone.now(),
                is_2fa_enabled=True,
                is_active=True
            )
        except User.DoesNotExist:
            raise InvalidTokenError('Invalid or expired token')

        if not verify_otp(user.otp_secret, otp_code):
            raise InvalidOTPError('Invalid OTP code')

        user.password_reset_token = None
        user.password_reset_expires = None
        user.last_login = timezone.now()
        user.save()

        tokens = self.get_tokens_for_user(user)

        return Response(
            StandardResponse.success(
                data={
                    'access_token': tokens['access'],
                    'refresh_token': tokens['refresh'],
                    'token_type': 'Bearer',
                    'expires_in': 3600,
                    'user': UserSerializer(user).data
                }
            ),
            status=status.HTTP_200_OK
        )
        
    @swagger_auto_schema(
        operation_summary="Logout",
        operation_description="Invalidate refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['refresh_token']
        ),
        security=bearer_security,
        responses={200: 'Logged out'}
    )    
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        """User logout endpoint."""
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            AuditLog.objects.create(
                user=request.user,
                action='LOGOUT',
                model_name='User',
                object_id=request.user.id,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            return Response(
                StandardResponse.success(message='Successfully logged out'),
                status=status.HTTP_200_OK
            )
        except TokenError:
            raise InvalidTokenError('Invalid refresh token')
    @swagger_auto_schema(
        operation_summary="Refresh JWT Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['refresh_token']
        ),
        responses={200: 'New access token'}
    )    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request):
        """Refresh access token."""
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                raise InvalidTokenError('Refresh token required')
            
            token = RefreshToken(refresh_token)
            
            return Response(
                StandardResponse.success(
                    data={
                        'access_token': str(token.access_token),
                        'token_type': 'Bearer',
                        'expires_in': 3600
                    }
                ),
                status=status.HTTP_200_OK
            )
        except TokenError:
            raise InvalidTokenError('Invalid or expired refresh token')
    @swagger_auto_schema(
        operation_summary="Request Password Reset",
        request_body=PasswordResetRequestSerializer,
        responses={200: 'Reset email sent'}
    )
    @action(detail=False, methods=['post'], url_path='password-reset')
    def password_reset(self, request):
        """Request password reset."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            token = generate_reset_token()
            user.password_reset_token = token
            user.password_reset_expires = timezone.now() + timedelta(hours=1)
            user.save()
            
            reset_link = create_password_reset_link(token)
            send_email_notification(
                to_email=user.email,
                subject='Password Reset Request',
                template_name='password_reset.html',
                context={
                    'user': user,
                    'reset_link': reset_link
                }
            )
        except User.DoesNotExist:
            pass
        
        return Response(
            StandardResponse.success(
                message='Password reset instructions sent to email'
            ),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Confirm Password Reset",
        request_body=PasswordResetConfirmSerializer,
        responses={200: 'Password reset successful'}
    )    
    @action(detail=False, methods=['post'], url_path='password-reset-confirm')
    def password_reset_confirm(self, request):
        """Confirm password reset."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(
                password_reset_token=token,
                password_reset_expires__gt=timezone.now(),
                is_active=True
            )
        except User.DoesNotExist:
            raise InvalidTokenError('Invalid or expired reset token')
        
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()
        
        return Response(
            StandardResponse.success(
                message='Password has been reset successfully'
            ),
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management operations."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        elif self.action == 'list':
            return [IsAdmin()]
        return [IsAuthenticated()]
    @swagger_auto_schema(
        operation_summary="List Users",
        manual_parameters=[
            openapi.Parameter('role', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        security=bearer_security
    )    
    def list(self, request):
        """List all users with filtering."""
        queryset = self.get_queryset()
        
        role = request.query_params.get('role')
        is_active = request.query_params.get('is_active')
        search = request.query_params.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Create User",
        request_body=UserCreateSerializer,
        security=bearer_security
    )    
    def create(self, request):
        """Create new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='User created successfully',
                data=UserSerializer(user).data
            ),
            status=status.HTTP_201_CREATED
        )
    @swagger_auto_schema(
        operation_summary="Update User",
        request_body=UserUpdateSerializer,
        security=bearer_security
    )
    def update(self, request, pk=None):
        """Update user."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='User updated successfully',
                data=UserSerializer(user).data
            ),
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        """Delete user."""
        user = self.get_object()
        
        if hasattr(user, 'student_profile'):
            student = user.student_profile
            if student.enrollments.filter(status='ENROLLED').exists():
                return Response(
                    StandardResponse.error(
                        message='Cannot delete user with active enrollments',
                        code='USER_HAS_DEPENDENCIES'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        user.delete()
        
        return Response(
            StandardResponse.success(message='User deleted successfully'),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Assign Role",
        request_body=RoleAssignSerializer,
        security=bearer_security,
        responses={200: 'Role assigned'}
    )    
    @action(detail=True, methods=['post'], url_path='assign-role', permission_classes=[IsAdmin])
    def assign_role(self, request, pk=None):
        """Assign role to user."""
        user = self.get_object()
        serializer = RoleAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.role = serializer.validated_data['role']
        user.save()
        
        return Response(
            StandardResponse.success(
                message='Role assigned successfully',
                data=UserSerializer(user).data
            ),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Get Current User",
        security=bearer_security
    )    
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Enable 2FA",
        operation_description="Generate QR code for authenticator app",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
        ),
        security=bearer_security,
        responses={200: 'QR Code generated'}
    )    
    @action(detail=False, methods=['post'], url_path='enable-2fa', permission_classes=[IsAuthenticated])
    def enable_2fa(self, request):
        """Enable 2FA for user."""
        user = request.user
        
        if user.is_2fa_enabled:
            return Response(
                StandardResponse.error(
                    message='2FA is already enabled',
                    code='2FA_ALREADY_ENABLED'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = Enable2FASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp_secret = serializer.validated_data['otp_secret']
        qr_code = generate_qr_code(user, otp_secret)
        
        return Response(
            StandardResponse.success(
                data={
                    'otp_secret': otp_secret,
                    'qr_code': qr_code,
                    'message': 'Scan QR code with authenticator app and verify'
                }
            ),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Verify 2FA Setup",
        request_body=Verify2FASerializer,
        security=bearer_security,
        responses={200: '2FA enabled'}
    )    
    @action(detail=False, methods=['post'], url_path='verify-2fa-setup', permission_classes=[IsAuthenticated])
    def verify_2fa_setup(self, request):
        """Verify and confirm 2FA setup."""
        user = request.user
        serializer = Verify2FASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.otp_secret = serializer.validated_data['otp_secret']
        user.is_2fa_enabled = True
        user.save()
        
        return Response(
            StandardResponse.success(
                message='2FA enabled successfully'
            ),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
        operation_summary="Disable 2FA",
        security=bearer_security,
        responses={200: '2FA disabled'}
    )    
    @action(detail=False, methods=['post'], url_path='disable-2fa', permission_classes=[IsAuthenticated])
    def disable_2fa(self, request):
        """Disable 2FA for user."""
        user = request.user
        
        if not user.is_2fa_enabled:
            return Response(
                StandardResponse.error(
                    message='2FA is not enabled',
                    code='2FA_NOT_ENABLED'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_2fa_enabled = False
        user.otp_secret = None
        user.save()
        
        return Response(
            StandardResponse.success(
                message='2FA disabled successfully'
            ),
            status=status.HTTP_200_OK
        )