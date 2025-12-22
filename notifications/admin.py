"""
Django admin configuration for notifications app.
"""
from django.contrib import admin
from notifications.models import Notification, Message, StudentRequest


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = [
        'title', 'recipient', 'notification_type',
        'is_read', 'priority', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'priority', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('recipient', 'notification_type', 'title', 'message', 'priority')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model."""
    
    list_display = [
        'subject', 'sender', 'recipient',
        'is_read', 'created_at'
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = [
        'subject', 'body',
        'sender__username', 'recipient__username'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Message Info', {
            'fields': ('sender', 'recipient', 'subject', 'body')
        }),
        ('Status', {
            'fields': ('is_read', 'parent_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StudentRequest)
class StudentRequestAdmin(admin.ModelAdmin):
    """Admin configuration for StudentRequest model."""
    
    list_display = [
        'student', 'request_type', 'subject',
        'status', 'processed_by', 'created_at'
    ]
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = [
        'subject', 'description',
        'student__student_id', 'student__user__username'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('student', 'request_type', 'subject', 'description')
        }),
        ('Processing', {
            'fields': ('status', 'processed_by', 'response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make student field readonly when editing."""
        if obj:  # Editing an existing object
            return self.readonly_fields + ['student']
        return self.readonly_fields