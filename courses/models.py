"""
Course, Class, Room, and Exam models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Course(models.Model):
    """
    Course definition.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_code = models.CharField(max_length=20, unique=True, db_index=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.IntegerField(validators=[MinValueValidator(1)])
    department = models.CharField(max_length=100, db_index=True)
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for'
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['course_code']
        indexes = [
            models.Index(fields=['course_code']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Room(models.Model):
    """
    Physical room/location for classes.
    """
    
    ROOM_TYPE_CHOICES = [
        ('CLASSROOM', 'Classroom'),
        ('LAB', 'Laboratory'),
        ('LECTURE_HALL', 'Lecture Hall'),
        ('SEMINAR', 'Seminar Room'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_number = models.CharField(max_length=20, unique=True, db_index=True)
    building = models.CharField(max_length=100)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    equipment = models.JSONField(default=list, blank=True)
    is_available = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rooms'
        ordering = ['building', 'room_number']
        indexes = [
            models.Index(fields=['room_number']),
            models.Index(fields=['building']),
        ]
    
    def __str__(self):
        return f"{self.building} - {self.room_number}"


class Class(models.Model):
    """
    Class instance of a course in a specific semester.
    """
    
    SEMESTER_CHOICES = [
        ('FALL', 'Fall'),
        ('SPRING', 'Spring'),
        ('SUMMER', 'Summer'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='taught_classes',
        limit_choices_to={'role': 'INSTRUCTOR'}
    )
    
    class_code = models.CharField(max_length=20, unique=True, db_index=True)
    section = models.CharField(max_length=10)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.IntegerField()
    
    max_capacity = models.IntegerField(validators=[MinValueValidator(1)])
    current_enrollment = models.IntegerField(default=0)
    
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes'
    )
    schedule = models.JSONField(
        default=list,
        help_text='Array of {day, start_time, end_time}'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'classes'
        ordering = ['-academic_year', 'semester', 'class_code']
        verbose_name_plural = 'Classes'
        indexes = [
            models.Index(fields=['class_code']),
            models.Index(fields=['semester', 'academic_year']),
            models.Index(fields=['instructor']),
        ]
    
    def __str__(self):
        return f"{self.class_code} - {self.course.course_name}"
    
    @property
    def available_seats(self):
        """Calculate available seats."""
        return self.max_capacity - self.current_enrollment
    
    @property
    def is_full(self):
        """Check if class is full."""
        return self.current_enrollment >= self.max_capacity
    
    def increment_enrollment(self):
        """Increment enrollment count."""
        self.current_enrollment += 1
        if self.is_full:
            self.status = 'CLOSED'
        self.save()
    
    def decrement_enrollment(self):
        """Decrement enrollment count."""
        if self.current_enrollment > 0:
            self.current_enrollment -= 1
            if self.status == 'CLOSED' and not self.is_full:
                self.status = 'OPEN'
            self.save()


class Exam(models.Model):
    """
    Exam schedule for a class.
    """
    
    EXAM_TYPE_CHOICES = [
        ('MIDTERM', 'Midterm'),
        ('FINAL', 'Final'),
        ('QUIZ', 'Quiz'),
        ('PROJECT', 'Project'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    exam_date = models.DateTimeField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams'
    )
    total_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    instructions = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exams'
        ordering = ['exam_date']
        indexes = [
            models.Index(fields=['class_instance', 'exam_type']),
            models.Index(fields=['exam_date']),
        ]
    
    def __str__(self):
        return f"{self.class_instance.class_code} - {self.get_exam_type_display()}"