"""
Django admin configuration for grades app.
"""
from django.contrib import admin
from grades.models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin configuration for Grade model."""
    
    list_display = [
        'get_student_id', 'get_student_name', 'get_class_code',
        'assignment_name', 'get_percentage', 'weight_percentage',
        'get_graded_by', 'graded_date'
    ]
    list_filter = [
        'enrollment__class_instance__semester',
        'enrollment__class_instance__academic_year',
        'exam__exam_type'
    ]
    search_fields = [
        'enrollment__student__student_id',
        'enrollment__student__user__first_name',
        'enrollment__student__user__last_name',
        'enrollment__class_instance__class_code',
        'assignment_name'
    ]
    readonly_fields = ['graded_by', 'graded_date', 'created_at', 'updated_at']
    date_hierarchy = 'graded_date'
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('enrollment', 'exam', 'assignment_name')
        }),
        ('Marks', {
            'fields': ('marks_obtained', 'total_marks', 'weight_percentage')
        }),
        ('Grading Details', {
            'fields': ('graded_by', 'graded_date', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
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
    
    def get_percentage(self, obj):
        return f"{obj.percentage:.2f}%"
    get_percentage.short_description = 'Score'
    
    def get_graded_by(self, obj):
        return obj.graded_by.full_name if obj.graded_by else 'N/A'
    get_graded_by.short_description = 'Graded By'