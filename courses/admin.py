"""
Django admin configuration for courses app.
"""
from django.contrib import admin
from courses.models import Course, Class, Room, Exam


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    
    list_display = [
        'course_code', 'course_name', 'credits',
        'department', 'is_active', 'created_at'
    ]
    list_filter = ['department', 'is_active', 'credits']
    search_fields = ['course_code', 'course_name', 'description']
    filter_horizontal = ['prerequisites']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('course_code', 'course_name', 'description', 'credits', 'department')
        }),
        ('Prerequisites', {
            'fields': ('prerequisites',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """Admin configuration for Class model."""
    
    list_display = [
        'class_code', 'get_course_name', 'section',
        'get_instructor_name', 'semester', 'academic_year',
        'current_enrollment', 'max_capacity', 'status'
    ]
    list_filter = ['semester', 'academic_year', 'status']
    search_fields = [
        'class_code', 'course__course_code', 'course__course_name',
        'instructor__first_name', 'instructor__last_name'
    ]
    readonly_fields = ['current_enrollment', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Class Information', {
            'fields': ('course', 'class_code', 'section')
        }),
        ('Schedule', {
            'fields': ('semester', 'academic_year', 'instructor', 'room', 'schedule')
        }),
        ('Capacity', {
            'fields': ('max_capacity', 'current_enrollment', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_course_name(self, obj):
        return obj.course.course_name
    get_course_name.short_description = 'Course'
    
    def get_instructor_name(self, obj):
        return obj.instructor.full_name if obj.instructor else 'N/A'
    get_instructor_name.short_description = 'Instructor'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin configuration for Room model."""
    
    list_display = [
        'room_number', 'building', 'capacity',
        'room_type', 'is_available'
    ]
    list_filter = ['room_type', 'is_available', 'building']
    search_fields = ['room_number', 'building']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room_number', 'building', 'capacity', 'room_type')
        }),
        ('Equipment', {
            'fields': ('equipment',)
        }),
        ('Availability', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin configuration for Exam model."""
    
    list_display = [
        'get_class_code', 'exam_type', 'exam_date',
        'duration_minutes', 'get_room', 'total_marks'
    ]
    list_filter = ['exam_type', 'exam_date']
    search_fields = [
        'class_instance__class_code',
        'class_instance__course__course_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Exam Information', {
            'fields': ('class_instance', 'exam_type', 'total_marks')
        }),
        ('Schedule', {
            'fields': ('exam_date', 'duration_minutes', 'room')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_class_code(self, obj):
        return obj.class_instance.class_code
    get_class_code.short_description = 'Class'
    
    def get_room(self, obj):
        return f"{obj.room.building} - {obj.room.room_number}" if obj.room else 'TBD'
    get_room.short_description = 'Room'