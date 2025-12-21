"""
Custom permission classes for role-based access control.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAdminOrRegistrar(permissions.BasePermission):
    """Allow access to admin and registrar users."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['ADMIN', 'REGISTRAR']
        )


class IsInstructor(permissions.BasePermission):
    """Allow access only to instructor users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'INSTRUCTOR'


class IsStudent(permissions.BasePermission):
    """Allow access only to student users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to owner or admin only."""
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == 'ADMIN':
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is the user itself
        return obj == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Read-only for all authenticated users, write for admin only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.role == 'ADMIN'


class CanManageStudents(permissions.BasePermission):
    """Permission to manage student records."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_students()
        )


class CanGrade(permissions.BasePermission):
    """Permission to submit and manage grades."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_grade()
        )


class CanManageCourses(permissions.BasePermission):
    """Permission to manage courses."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_courses()
        )