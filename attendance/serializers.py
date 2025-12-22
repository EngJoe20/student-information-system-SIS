"""
Serializers for attendance management.
"""
from rest_framework import serializers
from attendance.models import Attendance
from students.models import Enrollment


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for attendance with full details."""
    
    student_name = serializers.CharField(source='enrollment.student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='enrollment.student.student_id', read_only=True)
    class_code = serializers.CharField(source='enrollment.class_instance.class_code', read_only=True)
    course_name = serializers.CharField(source='enrollment.class_instance.course.course_name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'enrollment', 'student_name', 'student_id',
            'class_code', 'course_name', 'date', 'status',
            'notes', 'recorded_by', 'recorded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'created_at', 'updated_at']


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for recording attendance."""
    
    class Meta:
        model = Attendance
        fields = ['enrollment', 'date', 'status', 'notes']
    
    def validate(self, attrs):
        """Validate attendance recording."""
        enrollment = attrs['enrollment']
        date = attrs['date']
        
        # Check if enrollment is active
        if enrollment.status != 'ENROLLED':
            raise serializers.ValidationError({
                'enrollment': 'Can only record attendance for active enrollments'
            })
        
        # Check if attendance already exists
        if Attendance.objects.filter(enrollment=enrollment, date=date).exists():
            raise serializers.ValidationError({
                'date': 'Attendance already recorded for this date'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create attendance record with recorded_by."""
        request = self.context.get('request')
        validated_data['recorded_by'] = request.user
        return super().create(validated_data)


class AttendanceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating attendance."""
    
    class Meta:
        model = Attendance
        fields = ['status', 'notes']


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance recording."""
    
    class_id = serializers.UUIDField()
    date = serializers.DateField()
    attendance_records = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_attendance_records(self, value):
        """Validate attendance records format."""
        for record in value:
            if 'enrollment_id' not in record or 'status' not in record:
                raise serializers.ValidationError(
                    'Each record must have enrollment_id and status'
                )
            
            if record['status'] not in ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED']:
                raise serializers.ValidationError(
                    f'Invalid status: {record["status"]}'
                )
        
        return value
    
    def create(self, validated_data):
        """Create multiple attendance records."""
        from courses.models import Class
        
        class_id = validated_data['class_id']
        date = validated_data['date']
        records = validated_data['attendance_records']
        request = self.context.get('request')
        
        # Get class
        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            raise serializers.ValidationError({'class_id': 'Class not found'})
        
        # Create attendance records
        created_records = []
        for record in records:
            enrollment = Enrollment.objects.get(id=record['enrollment_id'])
            
            # Check if already exists
            attendance, created = Attendance.objects.get_or_create(
                enrollment=enrollment,
                date=date,
                defaults={
                    'status': record['status'],
                    'notes': record.get('notes', ''),
                    'recorded_by': request.user
                }
            )
            
            if not created:
                # Update existing
                attendance.status = record['status']
                attendance.notes = record.get('notes', '')
                attendance.save()
            
            created_records.append(attendance)
        
        return {
            'class_id': class_id,
            'date': date,
            'total_records': len(created_records),
            'recorded_by': request.user.full_name
        }


class AttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary."""
    
    total_days = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)