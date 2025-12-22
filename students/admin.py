"""
Django admin configuration for students app.
"""
from django.contrib import admin
from students.models import Student, Enrollment


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model."""
    
    list_display = [
        'student_id', 'get_full_name', 'academic_status',
        'gpa', 'enrollment_date', 'created_at'
    ]
    list_filter = ['academic_status', 'gender', 'enrollment_date']
    search_fields = [
        'student_id', 'user__first_name', 'user__last_name',
        'user__email'
    ]
    readonly_fields = ['gpa', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Student Information', {
            'fields': ('student_id', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Academic Information', {
            'fields': (
                'enrollment_date', 'graduation_date', 'academic_status', 'gpa'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Full Name'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Enrollment model."""
    
    list_display = [
        'get_student_id', 'get_student_name', 'get_class_code',
        'status', 'grade', 'enrollment_date'
    ]
    list_filter = ['status', 'class_instance__semester', 'class_instance__academic_year']
    search_fields = [
        'student__student_id', 'student__user__first_name',
        'student__user__last_name', 'class_instance__class_code'
    ]
    readonly_fields = ['enrollment_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'class_instance', 'enrollment_date', 'status')
        }),
        ('Grades', {
            'fields': ('grade', 'grade_points', 'midterm_grade', 'final_grade')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'
    
    def get_student_name(self, obj):
        return obj.student.user.full_name
    get_student_name.short_description = 'Student Name'
    
    def get_class_code(self, obj):
        return obj.class_instance.class_code
    get_class_code.short_description = 'Class Code'