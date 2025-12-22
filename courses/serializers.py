"""
Serializers for course management.
"""
from rest_framework import serializers
from courses.models import Course, Class, Room, Exam


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for course."""
    
    prerequisites = serializers.SerializerMethodField()
    prerequisites_count = serializers.IntegerField(
        source='prerequisites.count',
        read_only=True
    )
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'description',
            'credits', 'department', 'prerequisites', 'prerequisites_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_prerequisites(self, obj):
        """Get prerequisite courses."""
        return [
            {
                'id': str(prereq.id),
                'course_code': prereq.course_code,
                'course_name': prereq.course_name
            }
            for prereq in obj.prerequisites.all()
        ]


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating courses."""
    
    prerequisite_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'description',
            'credits', 'department', 'prerequisite_ids', 'is_active'
        ]
    
    def create(self, validated_data):
        """Create course with prerequisites."""
        prerequisite_ids = validated_data.pop('prerequisite_ids', [])
        course = Course.objects.create(**validated_data)
        
        if prerequisite_ids:
            prerequisites = Course.objects.filter(id__in=prerequisite_ids)
            course.prerequisites.set(prerequisites)
        
        return course


class CourseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating courses."""
    
    prerequisite_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Course
        fields = [
            'course_name', 'description', 'credits', 'department',
            'prerequisite_ids', 'is_active'
        ]
    
    def update(self, instance, validated_data):
        """Update course with prerequisites."""
        prerequisite_ids = validated_data.pop('prerequisite_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if prerequisite_ids is not None:
            prerequisites = Course.objects.filter(id__in=prerequisite_ids)
            instance.prerequisites.set(prerequisites)
        
        return instance


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for course lists."""
    
    prerequisites_count = serializers.IntegerField(
        source='prerequisites.count',
        read_only=True
    )
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'credits',
            'department', 'is_active', 'prerequisites_count'
        ]


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for room."""
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'building', 'capacity',
            'room_type', 'equipment', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating rooms."""
    
    class Meta:
        model = Room
        fields = [
            'room_number', 'building', 'capacity',
            'room_type', 'equipment', 'is_available'
        ]


class ClassScheduleField(serializers.JSONField):
    """Custom field for class schedule validation."""
    
    def to_internal_value(self, data):
        """Validate schedule format."""
        if not isinstance(data, list):
            raise serializers.ValidationError('Schedule must be a list')
        
        valid_days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for item in data:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Each schedule item must be a dictionary')
            
            if 'day' not in item or 'start_time' not in item or 'end_time' not in item:
                raise serializers.ValidationError(
                    'Each schedule must have day, start_time, and end_time'
                )
            
            if item['day'].upper() not in valid_days:
                raise serializers.ValidationError(f'Invalid day: {item["day"]}')
        
        return data


class ClassSerializer(serializers.ModelSerializer):
    """Serializer for class with full details."""
    
    course = CourseSerializer(read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    room_info = RoomSerializer(source='room', read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'course', 'instructor', 'instructor_name',
            'class_code', 'section', 'semester', 'academic_year',
            'max_capacity', 'current_enrollment', 'available_seats',
            'room', 'room_info', 'schedule', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_enrollment', 'created_at', 'updated_at']


class ClassCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating classes."""
    
    schedule = ClassScheduleField()
    
    class Meta:
        model = Class
        fields = [
            'course', 'instructor', 'class_code', 'section',
            'semester', 'academic_year', 'max_capacity',
            'room', 'schedule'
        ]
    
    def validate(self, attrs):
        """Validate class creation."""
        # Check if class code is unique
        if Class.objects.filter(class_code=attrs['class_code']).exists():
            raise serializers.ValidationError({
                'class_code': 'Class code already exists'
            })
        
        # Validate instructor role
        instructor = attrs.get('instructor')
        if instructor and instructor.role != 'INSTRUCTOR':
            raise serializers.ValidationError({
                'instructor': 'Selected user is not an instructor'
            })
        
        # Check room availability if provided
        room = attrs.get('room')
        if room:
            if attrs['max_capacity'] > room.capacity:
                raise serializers.ValidationError({
                    'max_capacity': f'Exceeds room capacity of {room.capacity}'
                })
            
            if not room.is_available:
                raise serializers.ValidationError({
                    'room': 'Room is not available'
                })
        
        return attrs


class ClassUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating classes."""
    
    schedule = ClassScheduleField(required=False)
    
    class Meta:
        model = Class
        fields = [
            'instructor', 'section', 'max_capacity',
            'room', 'schedule', 'status'
        ]
    
    def validate_max_capacity(self, value):
        """Validate max capacity doesn't go below current enrollment."""
        if self.instance and value < self.instance.current_enrollment:
            raise serializers.ValidationError(
                f'Cannot reduce capacity below current enrollment of {self.instance.current_enrollment}'
            )
        return value


class ClassListSerializer(serializers.ModelSerializer):
    """Simplified serializer for class lists."""
    
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    credits = serializers.IntegerField(source='course.credits', read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'class_code', 'course_code', 'course_name',
            'credits', 'section', 'instructor_name',
            'semester', 'academic_year', 'max_capacity',
            'current_enrollment', 'available_seats', 'status'
        ]


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for exam."""
    
    class_code = serializers.CharField(source='class_instance.class_code', read_only=True)
    course_name = serializers.CharField(source='class_instance.course.course_name', read_only=True)
    room_info = RoomSerializer(source='room', read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            'id', 'class_instance', 'class_code', 'course_name',
            'exam_type', 'exam_date', 'duration_minutes',
            'room', 'room_info', 'total_marks', 'instructions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating exams."""
    
    class Meta:
        model = Exam
        fields = [
            'class_instance', 'exam_type', 'exam_date',
            'duration_minutes', 'room', 'total_marks', 'instructions'
        ]
    
    def validate(self, attrs):
        """Validate exam scheduling."""
        room = attrs.get('room')
        exam_date = attrs.get('exam_date')
        duration = attrs.get('duration_minutes')
        
        if room and exam_date and duration:
            # Check for room conflicts
            from datetime import timedelta
            end_time = exam_date + timedelta(minutes=duration)
            
            conflicting_exams = Exam.objects.filter(
                room=room,
                exam_date__lt=end_time,
                exam_date__gte=exam_date
            )
            
            if self.instance:
                conflicting_exams = conflicting_exams.exclude(id=self.instance.id)
            
            if conflicting_exams.exists():
                raise serializers.ValidationError({
                    'room': 'Room is already booked for another exam at this time'
                })
        
        return attrs