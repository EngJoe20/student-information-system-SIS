"""
Views for student management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from students.models import Student, Enrollment
from students.serializers import (
    StudentSerializer, StudentCreateSerializer, StudentUpdateSerializer,
    StudentListSerializer, EnrollmentSerializer, EnrollmentCreateSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrRegistrar, IsOwnerOrAdmin
from core.utils import StandardResponse
from core.pagination import StandardResultsPagination


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for student management."""
    
    queryset = Student.objects.select_related('user').all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        elif self.action == 'list':
            return StudentListSerializer
        return StudentSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'destroy']:
            return [IsAdminOrRegistrar()]
        elif self.action in ['update', 'partial_update']:
            return [IsAdminOrRegistrar()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Students can only see their own profile
        if user.role == 'STUDENT':
            return queryset.filter(user=user)
        
        return queryset
    
    def list(self, request):
        """
        List students with filtering.
        GET /api/v1/students/
        """
        queryset = self.get_queryset()
        
        # Apply filters
        academic_status = request.query_params.get('academic_status')
        search = request.query_params.get('search')
        
        if academic_status:
            queryset = queryset.filter(academic_status=academic_status)
        
        if search:
            queryset = queryset.filter(
                Q(student_id__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Order by
        order_by = request.query_params.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
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
        Create student with user account.
        POST /api/v1/students/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Student profile created successfully',
                data=StudentSerializer(student).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, pk=None):
        """
        Get student profile.
        GET /api/v1/students/{id}/
        """
        student = self.get_object()
        serializer = self.get_serializer(student)
        
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    
    def update(self, request, pk=None):
        """
        Update student profile.
        PUT /api/v1/students/{id}/
        """
        student = self.get_object()
        serializer = self.get_serializer(student, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Student profile updated successfully',
                data=StudentSerializer(student).data
            ),
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, pk=None):
        """
        Delete student.
        DELETE /api/v1/students/{id}/
        """
        student = self.get_object()
        
        # Check for active enrollments
        if student.enrollments.filter(status='ENROLLED').exists():
            return Response(
                StandardResponse.error(
                    message='Cannot delete student with active enrollments',
                    code='STUDENT_HAS_ACTIVE_ENROLLMENTS'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete user and student
        user = student.user
        student.delete()
        user.delete()
        
        return Response(
            StandardResponse.success(message='Student deleted successfully'),
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], url_path='enrollments')
    def enrollments(self, request, pk=None):
        """
        Get student enrollment history.
        GET /api/v1/students/{id}/enrollments/
        """
        student = self.get_object()
        
        # Apply filters
        semester = request.query_params.get('semester')
        academic_year = request.query_params.get('academic_year')
        enrollment_status = request.query_params.get('status')
        
        enrollments = student.enrollments.select_related(
            'class_instance',
            'class_instance__course',
            'class_instance__instructor'
        ).all()
        
        if semester:
            enrollments = enrollments.filter(class_instance__semester=semester)
        
        if academic_year:
            enrollments = enrollments.filter(
                class_instance__academic_year=academic_year
            )
        
        if enrollment_status:
            enrollments = enrollments.filter(status=enrollment_status)
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for enrollment management."""
    
    queryset = Enrollment.objects.select_related(
        'student',
        'student__user',
        'class_instance',
        'class_instance__course',
        'class_instance__instructor'
    ).all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return EnrollmentCreateSerializer
        return EnrollmentSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'destroy']:
            # Students can enroll/drop, admins/registrars can manage all
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Students can only see their own enrollments
        if user.role == 'STUDENT':
            return queryset.filter(student__user=user)
        
        # Instructors can see enrollments in their classes
        if user.role == 'INSTRUCTOR':
            return queryset.filter(class_instance__instructor=user)
        
        return queryset
    
    def create(self, request):
        """
        Enroll student in class.
        POST /api/v1/enrollments/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Students can only enroll themselves
        if request.user.role == 'STUDENT':
            student = Student.objects.get(user=request.user)
            if str(serializer.validated_data['student'].id) != str(student.id):
                return Response(
                    StandardResponse.error(
                        message='You can only enroll yourself',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        enrollment = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Student enrolled successfully',
                data=EnrollmentSerializer(enrollment).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, pk=None):
        """
        Drop enrollment.
        DELETE /api/v1/enrollments/{id}/
        """
        enrollment = self.get_object()
        
        # Check if student can drop
        if request.user.role == 'STUDENT':
            if enrollment.student.user != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only drop your own enrollments',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if already completed or failed
            if enrollment.status in ['COMPLETED', 'FAILED']:
                return Response(
                    StandardResponse.error(
                        message='Cannot drop completed or failed enrollment',
                        code='INVALID_OPERATION'
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update status to dropped and decrement class enrollment
        enrollment.status = 'DROPPED'
        enrollment.save()
        enrollment.class_instance.decrement_enrollment()
        
        return Response(
            StandardResponse.success(
                message='Enrollment dropped successfully',
                data=EnrollmentSerializer(enrollment).data
            ),
            status=status.HTTP_200_OK
        )