"""
Serializers for grade management.
"""
from rest_framework import serializers
from grades.models import Grade
from students.models import Enrollment


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for grade with full details."""
    
    student_name = serializers.CharField(source='enrollment.student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='enrollment.student.student_id', read_only=True)
    class_code = serializers.CharField(source='enrollment.class_instance.class_code', read_only=True)
    course_name = serializers.CharField(source='enrollment.class_instance.course.course_name', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    weighted_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'enrollment', 'exam', 'student_name', 'student_id',
            'class_code', 'course_name', 'assignment_name',
            'marks_obtained', 'total_marks', 'percentage',
            'weight_percentage', 'weighted_score',
            'graded_by', 'graded_by_name', 'graded_date',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'graded_by', 'graded_date', 'created_at', 'updated_at']


class GradeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating grades."""
    
    class Meta:
        model = Grade
        fields = [
            'enrollment', 'exam', 'assignment_name',
            'marks_obtained', 'total_marks', 'weight_percentage', 'comments'
        ]
    
    def validate(self, attrs):
        """Validate grade submission."""
        enrollment = attrs['enrollment']
        
        # Check if enrollment is active
        if enrollment.status not in ['ENROLLED', 'COMPLETED']:
            raise serializers.ValidationError({
                'enrollment': 'Can only grade active or completed enrollments'
            })
        
        # Validate marks
        if attrs['marks_obtained'] > attrs['total_marks']:
            raise serializers.ValidationError({
                'marks_obtained': 'Marks obtained cannot exceed total marks'
            })
        
        # Validate weight percentage
        if attrs['weight_percentage'] > 100:
            raise serializers.ValidationError({
                'weight_percentage': 'Weight percentage cannot exceed 100'
            })
        
        # Check if exam belongs to the same class
        exam = attrs.get('exam')
        if exam and exam.class_instance != enrollment.class_instance:
            raise serializers.ValidationError({
                'exam': 'Exam does not belong to this class'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create grade with graded_by."""
        request = self.context.get('request')
        validated_data['graded_by'] = request.user
        return super().create(validated_data)


class GradeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating grades."""
    
    class Meta:
        model = Grade
        fields = ['marks_obtained', 'comments']
    
    def validate_marks_obtained(self, value):
        """Validate marks don't exceed total."""
        if self.instance and value > self.instance.total_marks:
            raise serializers.ValidationError(
                f'Marks cannot exceed total marks of {self.instance.total_marks}'
            )
        return value


class FinalizeGradeSerializer(serializers.Serializer):
    """Serializer for finalizing course grades."""
    
    final_grade = serializers.ChoiceField(
        choices=['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']
    )


class StudentGradesSummarySerializer(serializers.Serializer):
    """Serializer for student grades summary."""
    
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    gpa = serializers.DecimalField(max_digits=3, decimal_places=2)
    semester_gpa = serializers.DecimalField(max_digits=3, decimal_places=2)
    courses = serializers.ListField()


class GradeStatisticsSerializer(serializers.Serializer):
    """Serializer for grade statistics."""
    
    total_students = serializers.IntegerField()
    average_grade = serializers.DecimalField(max_digits=5, decimal_places=2)
    median_grade = serializers.DecimalField(max_digits=5, decimal_places=2)
    grade_distribution = serializers.DictField()