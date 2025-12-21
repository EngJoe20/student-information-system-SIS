"""
Serializers for authentication and user management.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from accounts.models import User
from core.utils import generate_otp_secret, verify_otp


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    # full_name = serializers.CharField(source='full_name', read_only=True)
    full_name = serializers.CharField()

    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'is_active', 'is_2fa_enabled',
            'phone_number', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name',
            'last_name', 'role', 'phone_number', 'is_active'
        ]
    
    def create(self, validated_data):
        """Create user with hashed password."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'STUDENT'),
            phone_number=validated_data.get('phone_number', ''),
            is_active=validated_data.get('is_active', True)
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users."""
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role',
            'phone_number', 'is_active'
        ]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate credentials."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    'Invalid credentials',
                    code='INVALID_CREDENTIALS'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled',
                    code='ACCOUNT_DISABLED'
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            'Must include username and password',
            code='REQUIRED_FIELDS'
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists."""
        if not User.objects.filter(email=value, is_active=True).exists():
            # Don't reveal if email exists or not for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                'Passwords do not match',
                code='PASSWORD_MISMATCH'
            )
        return attrs


class Enable2FASerializer(serializers.Serializer):
    """Serializer for enabling 2FA."""
    
    def validate(self, attrs):
        """Generate OTP secret."""
        attrs['otp_secret'] = generate_otp_secret()
        return attrs


class Verify2FASerializer(serializers.Serializer):
    """Serializer for verifying 2FA setup."""
    
    otp_code = serializers.CharField(required=True, max_length=6)
    otp_secret = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Verify OTP code."""
        if not verify_otp(attrs['otp_secret'], attrs['otp_code']):
            raise serializers.ValidationError(
                'Invalid OTP code',
                code='INVALID_OTP'
            )
        return attrs


class Login2FASerializer(serializers.Serializer):
    """Serializer for 2FA login verification."""
    
    temp_token = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)


class RoleAssignSerializer(serializers.Serializer):
    """Serializer for assigning roles."""
    
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)