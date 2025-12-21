"""
Student and Enrollment models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    """
    Student profile extending User model.
    """
    
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]
    
    ACADEMIC_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('GRADUATED', 'Graduated'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Personal Information
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Address Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    
    # Academic Information
    enrollment_date = models.DateField()
    graduation_date = models.DateField(blank=True, null=True)
    academic_status = models.CharField(
        max_length=20,
        choices=ACADEMIC_STATUS_CHOICES,
        default='ACTIVE'
    )
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(4.00)]
    )
    
    # Profile
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['student_id']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['academic_status']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.user.full_name}"
    
    def update_gpa(self):
        """Calculate and update student's cumulative GPA."""
        completed_enrollments = self.enrollments.filter(
            status='COMPLETED',
            grade_points__isnull=False
        )
        
        if not completed_enrollments.exists():
            self.gpa = 0.00
        else:
            total_points = sum(
                enrollment.grade_points * enrollment.class_instance.course.credits
                for enrollment in completed_enrollments
            )
            total_credits = sum(
                enrollment.class_instance.course.credits
                for enrollment in completed_enrollments
            )
            self.gpa = total_points / total_credits if total_credits > 0 else 0.00
        
        self.save()


class Enrollment(models.Model):
    """
    Student enrollment in a class.
    """
    
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('DROPPED', 'Dropped'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    class_instance = models.ForeignKey(
        'courses.Class',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ENROLLED'
    )
    
    # Grades
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True, null=True)
    grade_points = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(4.00)]
    )
    midterm_grade = models.CharField(max_length=5, blank=True, null=True)
    final_grade = models.CharField(max_length=5, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollments'
        ordering = ['-enrollment_date']
        unique_together = ['student', 'class_instance']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['class_instance', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.class_instance.class_code}"
    
    def finalize_grade(self, letter_grade):
        """Finalize course grade and update student GPA."""
        grade_point_map = {
            'A+': 4.00, 'A': 4.00, 'B+': 3.50, 'B': 3.00,
            'C+': 2.50, 'C': 2.00, 'D': 1.00, 'F': 0.00
        }
        
        self.grade = letter_grade
        self.grade_points = grade_point_map.get(letter_grade, 0.00)
        self.status = 'COMPLETED' if letter_grade != 'F' else 'FAILED'
        self.save()
        
        # Update student GPA
        self.student.update_gpa()