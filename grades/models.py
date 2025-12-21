"""
Grade and assessment models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from students.models import Enrollment
from courses.models import Exam


class Grade(models.Model):
    """
    Individual grade/assessment for a student in a class.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grades'
    )
    
    assignment_name = models.CharField(max_length=200)
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MinValueValidator(100)],
        help_text='Weight of this assessment in final grade'
    )
    
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_assessments'
    )
    graded_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        ordering = ['-graded_date']
        indexes = [
            models.Index(fields=['enrollment']),
            models.Index(fields=['exam']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.assignment_name}"
    
    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.total_marks > 0:
            return (self.marks_obtained / self.total_marks) * 100
        return 0
    
    @property
    def weighted_score(self):
        """Calculate weighted score for final grade calculation."""
        return (self.percentage / 100) * self.weight_percentage