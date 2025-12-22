"""
Views for course management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from courses.models import Course, Class, Room, Exam
from courses.serializers import (
    CourseSerializer, CourseCreateSerializer, CourseUpdateSerializer,
    CourseListSerializer, ClassSerializer, ClassCreateSerializer,
    ClassUpdateSerializer, ClassListSerializer, RoomSerializer,
    RoomCreateUpdateSerializer, ExamSerializer, ExamCreateUpdateSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrReadOnly, IsAdminOrRegistrar
from core.utils import StandardResponse
from core.pagination import StandardResultsPagination

from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer
from drf_yasg.utils import swagger_auto_schema

from students.serializers import StudentListSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for course management."""
    
    queryset = Course.objects.prefetch_related('prerequisites').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return CourseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CourseUpdateSerializer
        elif self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    def list(self, request):
        """
        List courses with filtering.
        GET /api/v1/courses/
        """
        queryset = self.get_queryset()
        
        # Apply filters
        department = request.query_params.get('department')
        is_active = request.query_params.get('is_active')
        search = request.query_params.get('search')
        
        if department:
            queryset = queryset.filter(department=department)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        if search:
            queryset = queryset.filter(
                Q(course_code__icontains=search) |
                Q(course_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    
    def create(self, request):
        """
        Create course.
        POST /api/v1/courses/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Course created successfully',
                data=CourseSerializer(course).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, pk=None):
        """
        Get course details with active classes.
        GET /api/v1/courses/{id}/
        """
        course = self.get_object()
        serializer = self.get_serializer(course)
        data = serializer.data
        
        # Add active classes
        active_classes = course.classes.filter(status='OPEN').select_related(
            'instructor', 'room'
        )
        data['active_classes'] = ClassListSerializer(
            active_classes, many=True
        ).data
        
        return Response(
            StandardResponse.success(data=data),
            status=status.HTTP_200_OK
        )
    
    def update(self, request, pk=None):
        """
        Update course.
        PUT /api/v1/courses/{id}/
        """
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Course updated successfully',
                data=CourseSerializer(course).data
            ),
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        """
        Delete course.
        DELETE /api/v1/courses/{id}/
        """
        course = self.get_object()
        
        # Check for active classes
        if course.classes.filter(status__in=['OPEN', 'CLOSED']).exists():
            return Response(
                StandardResponse.error(
                    message='Cannot delete course with active classes',
                    code='COURSE_HAS_ACTIVE_CLASSES'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course.delete()
        
        return Response(
            StandardResponse.success(message='Course deleted successfully'),
            status=status.HTTP_200_OK
        )


class ClassViewSet(viewsets.ModelViewSet):
    """ViewSet for class management."""
    
    queryset = Class.objects.select_related(
        'course', 'instructor', 'room'
    ).all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return ClassCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClassUpdateSerializer
        elif self.action == 'list':
            return ClassListSerializer
        return ClassSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrRegistrar()]
        return [IsAuthenticated()]
    
    def list(self, request):
        """
        List classes with filtering.
        GET /api/v1/classes/
        """
        queryset = self.get_queryset()
        
        # Apply filters
        course_id = request.query_params.get('course_id')
        instructor_id = request.query_params.get('instructor_id')
        semester = request.query_params.get('semester')
        academic_year = request.query_params.get('academic_year')
        class_status = request.query_params.get('status')
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)
        
        if semester:
            queryset = queryset.filter(semester=semester)
        
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        
        if class_status:
            queryset = queryset.filter(status=class_status)
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    
    def create(self, request):
        """
        Create class.
        POST /api/v1/classes/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        class_instance = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Class created successfully',
                data=ClassSerializer(class_instance).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """
        Update class.
        PUT /api/v1/classes/{id}/
        """
        class_instance = self.get_object()
        serializer = self.get_serializer(class_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Class updated successfully',
                data=ClassSerializer(class_instance).data
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='timetable')
    def timetable(self, request):
        """
        Get class timetable.
        GET /api/v1/classes/timetable/
        """
        semester = request.query_params.get('semester')
        academic_year = request.query_params.get('academic_year')
        student_id = request.query_params.get('student_id')
        instructor_id = request.query_params.get('instructor_id')
        
        if not semester or not academic_year:
            return Response(
                StandardResponse.error(
                    message='semester and academic_year are required'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            semester=semester,
            academic_year=academic_year,
            status__in=['OPEN', 'CLOSED']
        )
        
        # Filter by student enrollments
        if student_id:
            queryset = queryset.filter(
                enrollments__student_id=student_id,
                enrollments__status='ENROLLED'
            )
        
        # Filter by instructor
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)
        
        # Organize by day
        timetable = {}
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for day in days:
            timetable[day] = []
        
        for class_instance in queryset:
            for schedule_item in class_instance.schedule:
                day = schedule_item['day'].upper()
                if day in timetable:
                    timetable[day].append({
                        'start_time': schedule_item['start_time'],
                        'end_time': schedule_item['end_time'],
                        'class': ClassListSerializer(class_instance).data
                    })
        
        # Sort each day by start time
        for day in timetable:
            timetable[day].sort(key=lambda x: x['start_time'])
        
        return Response(
            StandardResponse.success(
                data={
                    'semester': semester,
                    'academic_year': int(academic_year),
                    'schedule': [
                        {'day': day, 'time_slots': slots}
                        for day, slots in timetable.items()
                        if slots
                    ]
                }
            ),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
    method='get',
    operation_summary="Class Attendance",
    operation_description="Get attendance records for a class"
    )
    @action(detail=True, methods=['get'], url_path='attendance')
    def attendance(self, request, pk=None):
        """
        Get attendance records for a class.
        """
        class_instance = self.get_object()

        date = request.query_params.get('date')
        status_filter = request.query_params.get('status')

        attendance_qs = Attendance.objects.select_related(
            'student',
            'student__user'
        ).filter(class_instance=class_instance)

        if date:
            attendance_qs = attendance_qs.filter(date=date)

        if status_filter:
            attendance_qs = attendance_qs.filter(status=status_filter)

        serializer = AttendanceSerializer(attendance_qs, many=True)

        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    @swagger_auto_schema(
    method='get',
    operation_summary="Class Roster",
    operation_description="Get enrolled students in a class"
    )
    @action(detail=True, methods=['get'], url_path='roster')
    def roster(self, request, pk=None):
        """
        Get enrolled students in class.
        """
        class_instance = self.get_object()

        enrollments = class_instance.enrollments.select_related(
            'student',
            'student__user'
        ).filter(status='ENROLLED')

        students = [e.student for e in enrollments]

        serializer = StudentListSerializer(students, many=True)

        return Response(
            StandardResponse.success(
                data={
                    "class": class_instance.id,
                    "count": len(students),
                    "students": serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet for room management."""
    
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action in ['create', 'update', 'partial_update']:
            return RoomCreateUpdateSerializer
        return RoomSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def create(self, request):
        """
        Create room.
        POST /api/v1/rooms/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Room created successfully',
                data=RoomSerializer(room).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """
        Update room.
        PUT /api/v1/rooms/{id}/
        """
        room = self.get_object()
        serializer = self.get_serializer(room, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Room updated successfully',
                data=RoomSerializer(room).data
            ),
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        """
        Delete room.
        DELETE /api/v1/rooms/{id}/
        """
        room = self.get_object()
        
        # Check for active classes
        if room.classes.filter(status__in=['OPEN', 'CLOSED']).exists():
            return Response(
                StandardResponse.error(
                    message='Cannot delete room with active classes',
                    code='ROOM_HAS_ACTIVE_CLASSES'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room.delete()
        
        return Response(
            StandardResponse.success(message='Room deleted successfully'),
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        """
        Get available rooms.
        GET /api/v1/rooms/available/
        """
        queryset = self.get_queryset().filter(is_available=True)
        
        # Apply filters
        capacity_min = request.query_params.get('capacity_min')
        room_type = request.query_params.get('room_type')
        
        if capacity_min:
            queryset = queryset.filter(capacity__gte=capacity_min)
        
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for exam management."""
    
    queryset = Exam.objects.select_related(
        'class_instance',
        'class_instance__course',
        'room'
    ).all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action in ['create', 'update', 'partial_update']:
            return ExamCreateUpdateSerializer
        return ExamSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrRegistrar()]
        return [IsAuthenticated()]
    
    def list(self, request):
        """
        List exams with filtering.
        GET /api/v1/exams/
        """
        queryset = self.get_queryset()
        
        # Apply filters
        class_id = request.query_params.get('class_id')
        exam_type = request.query_params.get('exam_type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        student_id = request.query_params.get('student_id')
        
        if class_id:
            queryset = queryset.filter(class_instance_id=class_id)
        
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
        
        if start_date:
            queryset = queryset.filter(exam_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(exam_date__lte=end_date)
        
        if student_id:
            queryset = queryset.filter(
                class_instance__enrollments__student_id=student_id,
                class_instance__enrollments__status='ENROLLED'
            )
        
        # Order by exam date
        queryset = queryset.order_by('exam_date')
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    
    def create(self, request):
        """
        Create exam schedule.
        POST /api/v1/exams/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Exam scheduled successfully',
                data=ExamSerializer(exam).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """
        Update exam schedule.
        PUT /api/v1/exams/{id}/
        """
        exam = self.get_object()
        serializer = self.get_serializer(exam, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Exam schedule updated successfully',
                data=ExamSerializer(exam).data
            ),
            status=status.HTTP_200_OK
        )