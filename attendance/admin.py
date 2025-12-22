"""
Django admin configuration for attendance app.
"""
from django.contrib import admin
from attendance.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""
    
    list_display = [
        'get_student_id', 'get_student_name', 'get_class_code',
        'date', 'status', 'get_recorded_by', 'created_at'
    ]
    list_filter = ['status', 'date', 'enrollment__class_instance__semester']
    search_fields = [
        'enrollment__student__student_id',
        'enrollment__student__user__first_name',
        'enrollment__student__user__last_name',
        'enrollment__class_instance__class_code'
    ]
    readonly_fields = ['recorded_by', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('enrollment', 'date', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Tracking', {
            'fields': ('recorded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_id(self, obj):
        return obj.enrollment.student.student_id
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'enrollment__student__student_id'
    
    def get_student_name(self, obj):
        return obj.enrollment.student.user.full_name
    get_student_name.short_description = 'Student Name'
    
    def get_class_code(self, obj):
        return obj.enrollment.class_instance.class_code
    get_class_code.short_description = 'Class'
    get_class_code.admin_order_field = 'enrollment__class_instance__class_code'
    
    def get_recorded_by(self, obj):
        return obj.recorded_by.full_name if obj.recorded_by else 'N/A'
    get_recorded_by.short_description = 'Recorded By'