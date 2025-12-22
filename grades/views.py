"""
Views for grade management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from decimal import Decimal
import statistics

from grades.models import Grade
from grades.serializers import (
    GradeSerializer, GradeCreateSerializer, GradeUpdateSerializer,
    FinalizeGradeSerializer, StudentGradesSummarySerializer,
    GradeStatisticsSerializer
)
from students.models import Student, Enrollment
from courses.models import Class
from accounts.permissions import IsAdmin, CanGrade
from core.utils import StandardResponse
from core.pagination import StandardResultsPagination


class GradeViewSet(viewsets.ModelViewSet):
    """ViewSet for grade management."""
    
    queryset = Grade.objects.select_related(
        'enrollment',
        'enrollment__student',
        'enrollment__student__user',
        'enrollment__class_instance',
        'enrollment__class_instance__course',
        'exam',
        'graded_by'
    ).all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return GradeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GradeUpdateSerializer
        elif self.action == 'finalize_grade':
            return FinalizeGradeSerializer
        return GradeSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'finalize_grade']:
            return [CanGrade()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Students can only see their own grades
        if user.role == 'STUDENT':
            return queryset.filter(enrollment__student__user=user)
        
        # Instructors can see grades in their classes
        if user.role == 'INSTRUCTOR':
            return queryset.filter(enrollment__class_instance__instructor=user)
        
        return queryset
    
    def create(self, request):
        """
        Submit grade.
        POST /api/v1/grades/
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Check if instructor can grade this class
        if request.user.role == 'INSTRUCTOR':
            enrollment = serializer.validated_data['enrollment']
            if enrollment.class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only grade your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        grade = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Grade submitted successfully',
                data=GradeSerializer(grade).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, **kwargs):
        """
        Update grade.
        PUT /api/v1/grades/{id}/
        """
        grade = self.get_object()
        
        # Check if instructor can update
        if request.user.role == 'INSTRUCTOR':
            if grade.enrollment.class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only update grades for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        #FIX: making partial as pagination        
        partial= kwargs.pop('partial',False)
        
        serializer = self.get_serializer(grade, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Grade updated successfully',
                data=GradeSerializer(grade).data
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_grades(self, request, student_id=None):
        """
        Get student grades.
        GET /api/v1/grades/student/{student_id}/
        """
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                StandardResponse.error(
                    message='Student not found',
                    code='RESOURCE_NOT_FOUND'
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if request.user.role == 'STUDENT' and student.user != request.user:
            return Response(
                StandardResponse.error(
                    message='You can only view your own grades',
                    code='PERMISSION_DENIED'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Apply filters
        class_id = request.query_params.get('class_id')
        semester = request.query_params.get('semester')
        academic_year = request.query_params.get('academic_year')
        
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related('class_instance__course', 'class_instance__instructor')
        
        if class_id:
            enrollments = enrollments.filter(class_instance_id=class_id)
        
        if semester:
            enrollments = enrollments.filter(class_instance__semester=semester)
        
        if academic_year:
            enrollments = enrollments.filter(class_instance__academic_year=academic_year)
        
        # Calculate semester GPA if semester and year provided
        semester_gpa = Decimal('0.00')
        if semester and academic_year:
            semester_enrollments = enrollments.filter(
                status='COMPLETED',
                grade_points__isnull=False
            )
            if semester_enrollments.exists():
                total_points = sum(
                    e.grade_points * e.class_instance.course.credits
                    for e in semester_enrollments
                )
                total_credits = sum(
                    e.class_instance.course.credits
                    for e in semester_enrollments
                )
                semester_gpa = total_points / total_credits if total_credits > 0 else Decimal('0.00')
        
        # Build courses data
        courses = []
        for enrollment in enrollments:
            grades = Grade.objects.filter(enrollment=enrollment)
            
            courses.append({
                'class': {
                    'class_code': enrollment.class_instance.class_code,
                    'course_name': enrollment.class_instance.course.course_name,
                    'credits': enrollment.class_instance.course.credits,
                    'instructor_name': enrollment.class_instance.instructor.full_name if enrollment.class_instance.instructor else 'N/A'
                },
                'grades': GradeSerializer(grades, many=True).data,
                'final_grade': enrollment.grade,
                'grade_points': float(enrollment.grade_points) if enrollment.grade_points else None
            })
        
        return Response(
            StandardResponse.success(
                data={
                    'student': {
                        'id': str(student.id),
                        'student_id': student.student_id,
                        'name': student.user.full_name,
                        'gpa': float(student.gpa)
                    },
                    'semester_gpa': float(semester_gpa),
                    'courses': courses
                }
            ),
            status=status.HTTP_200_OK
        )
    
    @action(
        detail=False,
        methods=['post'],
        url_path='enrollment/(?P<enrollment_id>[^/.]+)/finalize'
    )
    def finalize_grade(self, request, enrollment_id=None):
        """
        Finalize course grade.
        POST /api/v1/grades/enrollment/{enrollment_id}/finalize/
        """
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)
        except Enrollment.DoesNotExist:
            return Response(
                StandardResponse.error(
                    message='Enrollment not found',
                    code='RESOURCE_NOT_FOUND'
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if request.user.role == 'INSTRUCTOR':
            if enrollment.class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only finalize grades for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Finalize grade
        enrollment.finalize_grade(serializer.validated_data['final_grade'])
        
        return Response(
            StandardResponse.success(
                message='Final grade submitted successfully',
                data={
                    'enrollment_id': str(enrollment.id),
                    'student_name': enrollment.student.user.full_name,
                    'class_code': enrollment.class_instance.class_code,
                    'final_grade': enrollment.grade,
                    'grade_points': float(enrollment.grade_points),
                    'status': enrollment.status
                }
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='class/(?P<class_id>[^/.]+)/statistics')
    def class_statistics(self, request, class_id=None):
        """
        Get grade statistics for a class.
        GET /api/v1/grades/class/{class_id}/statistics/
        """
        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response(
                StandardResponse.error(
                    message='Class not found',
                    code='RESOURCE_NOT_FOUND'
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if request.user.role == 'INSTRUCTOR':
            if class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only view statistics for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get completed enrollments with grades
        enrollments = Enrollment.objects.filter(
            class_instance=class_instance,
            status='COMPLETED',
            grade__isnull=False
        ).select_related('student__user')
        
        if not enrollments.exists():
            return Response(
                StandardResponse.success(
                    data={
                        'class': {
                            'class_code': class_instance.class_code,
                            'course_name': class_instance.course.course_name
                        },
                        'statistics': {
                            'total_students': 0,
                            'message': 'No completed grades yet'
                        }
                    }
                ),
                status=status.HTTP_200_OK
            )
        
        # Calculate statistics
        grade_points = [float(e.grade_points) for e in enrollments]
        
        # Grade distribution
        grade_distribution = {
            'A+': enrollments.filter(grade='A+').count(),
            'A': enrollments.filter(grade='A').count(),
            'B+': enrollments.filter(grade='B+').count(),
            'B': enrollments.filter(grade='B').count(),
            'C+': enrollments.filter(grade='C+').count(),
            'C': enrollments.filter(grade='C').count(),
            'D': enrollments.filter(grade='D').count(),
            'F': enrollments.filter(grade='F').count(),
        }
        
        # Student grades details
        student_grades = []
        for enrollment in enrollments:
            grades = Grade.objects.filter(enrollment=enrollment)
            student_grades.append({
                'student_id': enrollment.student.student_id,
                'student_name': enrollment.student.user.full_name,
                'assignments': [
                    {
                        'assignment_name': g.assignment_name,
                        'marks_obtained': float(g.marks_obtained),
                        'total_marks': float(g.total_marks),
                        'percentage': float(g.percentage)
                    }
                    for g in grades
                ],
                'final_grade': enrollment.grade,
                'grade_points': float(enrollment.grade_points)
            })
        
        return Response(
            StandardResponse.success(
                data={
                    'class': {
                        'class_code': class_instance.class_code,
                        'course_name': class_instance.course.course_name,
                        'section': class_instance.section,
                        'instructor_name': class_instance.instructor.full_name if class_instance.instructor else 'N/A'
                    },
                    'semester': class_instance.semester,
                    'academic_year': class_instance.academic_year,
                    'statistics': {
                        'total_students': len(enrollments),
                        'average_grade': round(sum(grade_points) / len(grade_points), 2),
                        'median_grade': round(statistics.median(grade_points), 2),
                        'grade_distribution': grade_distribution
                    },
                    'student_grades': student_grades
                }
            ),
            status=status.HTTP_200_OK
        )