"""
User model and authentication-related models.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based access control.
    """
    
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('ADMIN', 'Administrator'),
        ('REGISTRAR', 'Registrar'),
        ('INSTRUCTOR', 'Instructor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Password reset fields
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    
    # 2FA fields
    otp_secret = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role):
        """Check if user has specific role."""
        return self.role == role
    
    def can_manage_students(self):
        """Check if user can manage students."""
        return self.role in ['ADMIN', 'REGISTRAR']
    
    def can_manage_courses(self):
        """Check if user can manage courses."""
        return self.role == 'ADMIN'
    
    def can_grade(self):
        """Check if user can submit grades."""
        return self.role in ['ADMIN', 'INSTRUCTOR']