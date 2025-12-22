"""
Serializers for student management.
"""
from rest_framework import serializers
from students.models import Student, Enrollment
from accounts.serializers import UserSerializer, UserCreateSerializer
from accounts.models import User


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student with user account."""
    
    user = UserCreateSerializer()
    
    class Meta:
        model = Student
        fields = [
            'address', 'city', 'state', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone',
            'phone_number', 'academic_status', 'profile_picture',
            'graduation_date'
        ]
    
    def create(self, validated_data):
        """Create user and student profile together."""
        user_data = validated_data.pop('user')
        user_data['role'] = 'STUDENT'  # Force student role
        
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            role='STUDENT',
            phone_number=user_data.get('phone_number', '')
        )
        
        # Create student profile
        student = Student.objects.create(user=user, **validated_data)
        return student


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for student profile."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'full_name', 'student_id', 'date_of_birth', 'gender',
            'address', 'city', 'state', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone',
            'enrollment_date', 'graduation_date', 'academic_status',
            'gpa', 'profile_picture', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'gpa', 'created_at', 'updated_at']


class StudentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating student profile."""
    
    phone_number = serializers.CharField(source='user.phone_number', required=False)
    
    class Meta:
        model = Student
        fields = [
            'address', 'city', 'state', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone',
            'phone_number', 'academic_status', 'profile_picture',
            'graduation_date'
        ]
    
    def update(self, instance, validated_data):
        """Update student and user phone number."""
        # Update user phone if provided
        user_data = validated_data.pop('user', {})
        if 'phone_number' in user_data:
            instance.user.phone_number = user_data['phone_number']
            instance.user.save()
        
        # Update student fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class StudentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for student lists."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'full_name', 'email',
            'academic_status', 'gpa', 'enrollment_date'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollment with full details."""
    
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    class_code = serializers.CharField(source='class_instance.class_code', read_only=True)
    course_code = serializers.CharField(source='class_instance.course.course_code', read_only=True)
    course_name = serializers.CharField(source='class_instance.course.course_name', read_only=True)
    credits = serializers.IntegerField(source='class_instance.course.credits', read_only=True)
    instructor_name = serializers.CharField(source='class_instance.instructor.full_name', read_only=True)
    semester = serializers.CharField(source='class_instance.semester', read_only=True)
    academic_year = serializers.IntegerField(source='class_instance.academic_year', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'class_instance', 'class_code', 'course_code', 'course_name',
            'credits', 'instructor_name', 'semester', 'academic_year',
            'enrollment_date', 'status', 'grade', 'grade_points',
            'midterm_grade', 'final_grade', 'created_at'
        ]
        read_only_fields = ['id', 'enrollment_date', 'created_at']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enrollments."""
    
    class Meta:
        model = Enrollment
        fields = ['student', 'class_instance']
    
    def validate(self, attrs):
        """Validate enrollment requirements."""
        student = attrs['student']
        class_instance = attrs['class_instance']
        
        # Check if already enrolled
        if Enrollment.objects.filter(
            student=student,
            class_instance=class_instance
        ).exists():
            raise serializers.ValidationError(
                'Student is already enrolled in this class'
            )
        
        # Check class capacity
        if class_instance.is_full:
            raise serializers.ValidationError(
                'Class is full',
                code='CLASS_FULL'
            )
        
        # Check prerequisites
        course = class_instance.course
        if course.prerequisites.exists():
            completed_courses = Enrollment.objects.filter(
                student=student,
                status='COMPLETED',
                class_instance__course__in=course.prerequisites.all()
            ).values_list('class_instance__course_id', flat=True)
            
            required_prereqs = set(course.prerequisites.values_list('id', flat=True))
            completed_prereqs = set(completed_courses)
            
            if not required_prereqs.issubset(completed_prereqs):
                missing = course.prerequisites.exclude(
                    id__in=completed_prereqs
                )
                raise serializers.ValidationError({
                    'message': 'Prerequisites not met',
                    'code': 'PREREQUISITES_NOT_MET',
                    'missing_prerequisites': [
                        {
                            'course_code': p.course_code,
                            'course_name': p.course_name
                        }
                        for p in missing
                    ]
                })
        
        # Check schedule conflicts
        existing_enrollments = Enrollment.objects.filter(
            student=student,
            status='ENROLLED',
            class_instance__semester=class_instance.semester,
            class_instance__academic_year=class_instance.academic_year
        ).select_related('class_instance')
        
        for enrollment in existing_enrollments:
            if self._has_schedule_conflict(
                enrollment.class_instance.schedule,
                class_instance.schedule
            ):
                raise serializers.ValidationError(
                    f'Schedule conflict with {enrollment.class_instance.class_code}',
                    code='SCHEDULE_CONFLICT'
                )
        
        return attrs
    
    def _has_schedule_conflict(self, schedule1, schedule2):
        """Check if two schedules conflict."""
        for s1 in schedule1:
            for s2 in schedule2:
                if s1['day'] == s2['day']:
                    # Check time overlap
                    start1 = s1['start_time']
                    end1 = s1['end_time']
                    start2 = s2['start_time']
                    end2 = s2['end_time']
                    
                    if (start1 < end2 and end1 > start2):
                        return True
        return False
    
    def create(self, validated_data):
        """Create enrollment and update class count."""
        enrollment = Enrollment.objects.create(**validated_data)
        enrollment.class_instance.increment_enrollment()
        return enrollment