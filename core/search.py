"""
Advanced search functionality across the system.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import User
from students.models import Student
from courses.models import Course, Class
from core.utils import StandardResponse

bearer_security = [{'Bearer': []}]


class GlobalSearchViewSet(viewsets.GenericViewSet):
    """Global search across all entities."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Global Search",
        operation_description="Search across students, courses, classes, and users",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True, description='Search query'),
            openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by type: student, course, class, user'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=10),
        ],
        security=bearer_security
    )
    @action(detail=False, methods=['get'], url_path='search')
    def global_search(self, request):
        """
        Global search across multiple entities.
        """
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        limit = int(request.query_params.get('limit', 10))
        
        if not query:
            return Response(
                StandardResponse.error(
                    message='Search query is required',
                    code='MISSING_QUERY'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'query': query,
            'total_results': 0,
            'results': {}
        }
        
        # Search Students
        if search_type in ['all', 'student']:
            students = Student.objects.filter(
                Q(student_id__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query)
            ).select_related('user')[:limit]
            
            results['results']['students'] = [
                {
                    'id': str(student.id),
                    'student_id': student.student_id,
                    'name': student.user.full_name,
                    'email': student.user.email,
                    'academic_status': student.get_academic_status_display(),
                    'type': 'student'
                }
                for student in students
            ]
            results['total_results'] += len(results['results']['students'])
        
        # Search Courses
        if search_type in ['all', 'course']:
            courses = Course.objects.filter(
                Q(course_code__icontains=query) |
                Q(course_name__icontains=query) |
                Q(description__icontains=query) |
                Q(department__icontains=query)
            )[:limit]
            
            results['results']['courses'] = [
                {
                    'id': str(course.id),
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'department': course.department,
                    'credits': course.credits,
                    'type': 'course'
                }
                for course in courses
            ]
            results['total_results'] += len(results['results']['courses'])
        
        # Search Classes
        if search_type in ['all', 'class']:
            classes = Class.objects.filter(
                Q(class_code__icontains=query) |
                Q(course__course_name__icontains=query) |
                Q(course__course_code__icontains=query) |
                Q(instructor__first_name__icontains=query) |
                Q(instructor__last_name__icontains=query)
            ).select_related('course', 'instructor')[:limit]
            
            results['results']['classes'] = [
                {
                    'id': str(class_obj.id),
                    'class_code': class_obj.class_code,
                    'course_name': class_obj.course.course_name,
                    'course_code': class_obj.course.course_code,
                    'instructor_name': class_obj.instructor.full_name,
                    'semester': class_obj.semester,
                    'academic_year': class_obj.academic_year,
                    'type': 'class'
                }
                for class_obj in classes
            ]
            results['total_results'] += len(results['results']['classes'])
        
        # Search Users (Admin only)
        if request.user.role == 'ADMIN' and search_type in ['all', 'user']:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )[:limit]
            
            results['results']['users'] = [
                {
                    'id': str(user.id),
                    'username': user.username,
                    'name': user.full_name,
                    'email': user.email,
                    'role': user.get_role_display(),
                    'type': 'user'
                }
                for user in users
            ]
            results['total_results'] += len(results['results']['users'])
        
        return Response(
            StandardResponse.success(data=results),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Advanced Student Search",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('academic_status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('enrollment_year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('gpa_min', openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
            openapi.Parameter('gpa_max', openapi.IN_QUERY, type=openapi.TYPE_NUMBER),
        ],
        security=bearer_security
    )
    @action(detail=False, methods=['get'], url_path='students/advanced')
    def advanced_student_search(self, request):
        """Advanced student search with multiple filters."""
        queryset = Student.objects.select_related('user').all()
        
        # Text search
        query = request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(student_id__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query)
            )
        
        # Academic status filter
        academic_status = request.query_params.get('academic_status')
        if academic_status:
            queryset = queryset.filter(academic_status=academic_status)
        
        # Enrollment year filter
        enrollment_year = request.query_params.get('enrollment_year')
        if enrollment_year:
            queryset = queryset.filter(enrollment_date__year=enrollment_year)
        
        # GPA filters
        gpa_min = request.query_params.get('gpa_min')
        if gpa_min:
            queryset = queryset.filter(gpa__gte=float(gpa_min))
        
        gpa_max = request.query_params.get('gpa_max')
        if gpa_max:
            queryset = queryset.filter(gpa__lte=float(gpa_max))
        
        # Pagination
        page = self.paginate_queryset(queryset)
        
        results = [
            {
                'id': str(student.id),
                'student_id': student.student_id,
                'name': student.user.full_name,
                'email': student.user.email,
                'academic_status': student.get_academic_status_display(),
                'gpa': float(student.gpa),
                'enrollment_date': student.enrollment_date
            }
            for student in (page if page else queryset)
        ]
        
        if page is not None:
            return self.get_paginated_response(results)
        
        return Response(
            StandardResponse.success(data=results),
            status=status.HTTP_200_OK
        )