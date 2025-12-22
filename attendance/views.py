"""
Views for attendance management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Case, When
from datetime import datetime, timedelta

from attendance.models import Attendance
from attendance.serializers import (
    AttendanceSerializer, AttendanceCreateSerializer,
    AttendanceUpdateSerializer, BulkAttendanceSerializer,
    AttendanceSummarySerializer
)
from students.models import Student, Enrollment
from courses.models import Class
from accounts.permissions import IsAdmin, CanGrade
from core.utils import StandardResponse
from core.pagination import StandardResultsPagination


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for attendance management."""
    
    queryset = Attendance.objects.select_related(
        'enrollment',
        'enrollment__student',
        'enrollment__student__user',
        'enrollment__class_instance',
        'enrollment__class_instance__course',
        'recorded_by'
    ).all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return AttendanceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AttendanceUpdateSerializer
        elif self.action == 'bulk_record':
            return BulkAttendanceSerializer
        return AttendanceSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'bulk_record']:
            return [CanGrade()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Students can only see their own attendance
        if user.role == 'STUDENT':
            return queryset.filter(enrollment__student__user=user)
        
        # Instructors can see attendance in their classes
        if user.role == 'INSTRUCTOR':
            return queryset.filter(enrollment__class_instance__instructor=user)
        
        return queryset
    
    def create(self, request):
        """
        Record attendance for single student.
        POST /api/v1/attendance/
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Check if instructor can record for this class
        if request.user.role == 'INSTRUCTOR':
            enrollment = serializer.validated_data['enrollment']
            if enrollment.class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only record attendance for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        attendance = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Attendance recorded successfully',
                data=AttendanceSerializer(attendance).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """
        Update attendance record.
        PUT /api/v1/attendance/{id}/
        """
        attendance = self.get_object()
        
        # Check if instructor can update
        if request.user.role == 'INSTRUCTOR':
            if attendance.enrollment.class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only update attendance for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(attendance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Attendance updated successfully',
                data=AttendanceSerializer(attendance).data
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='bulk-record')
    def bulk_record(self, request):
        """
        Record attendance for multiple students.
        POST /api/v1/attendance/bulk-record/
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Check if instructor can record for this class
        if request.user.role == 'INSTRUCTOR':
            from courses.models import Class
            class_instance = Class.objects.get(id=serializer.validated_data['class_id'])
            if class_instance.instructor != request.user:
                return Response(
                    StandardResponse.error(
                        message='You can only record attendance for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        result = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Attendance recorded successfully',
                data=result
            ),
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_attendance(self, request, student_id=None):
        """
        Get student attendance records.
        GET /api/v1/attendance/student/{student_id}/
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
                    message='You can only view your own attendance',
                    code='PERMISSION_DENIED'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Apply filters
        class_id = request.query_params.get('class_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        attendance_records = Attendance.objects.filter(
            enrollment__student=student
        ).select_related(
            'enrollment__class_instance__course'
        )
        
        if class_id:
            attendance_records = attendance_records.filter(
                enrollment__class_instance_id=class_id
            )
        
        if start_date:
            attendance_records = attendance_records.filter(date__gte=start_date)
        
        if end_date:
            attendance_records = attendance_records.filter(date__lte=end_date)
        
        # Calculate summary
        total_days = attendance_records.count()
        present = attendance_records.filter(status='PRESENT').count()
        absent = attendance_records.filter(status='ABSENT').count()
        late = attendance_records.filter(status='LATE').count()
        excused = attendance_records.filter(status='EXCUSED').count()
        
        attendance_percentage = (
            (present / total_days * 100) if total_days > 0 else 0
        )
        
        summary = {
            'total_days': total_days,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_percentage': round(attendance_percentage, 2)
        }
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        
        return Response(
            StandardResponse.success(
                data={
                    'student': {
                        'id': str(student.id),
                        'student_id': student.student_id,
                        'name': student.user.full_name
                    },
                    'attendance_summary': summary,
                    'records': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='class/(?P<class_id>[^/.]+)')
    def class_attendance(self, request, class_id=None):
        """
        Get class attendance for a specific date.
        GET /api/v1/attendance/class/{class_id}/
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
                        message='You can only view attendance for your own classes',
                        code='PERMISSION_DENIED'
                    ),
                    status=status.HTTP_403_FORBIDDEN
                )
        
        date = request.query_params.get('date')
        if not date:
            return Response(
                StandardResponse.error(message='date parameter is required'),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all enrollments for this class
        enrollments = Enrollment.objects.filter(
            class_instance=class_instance,
            status='ENROLLED'
        ).select_related('student', 'student__user')
        
        # Get attendance records for this date
        attendance_records = Attendance.objects.filter(
            enrollment__class_instance=class_instance,
            date=date
        )
        
        attendance_dict = {
            str(a.enrollment_id): a for a in attendance_records
        }
        
        # Build response data
        records = []
        for enrollment in enrollments:
            attendance = attendance_dict.get(str(enrollment.id))
            records.append({
                'enrollment_id': str(enrollment.id),
                'student': {
                    'id': str(enrollment.student.id),
                    'student_id': enrollment.student.student_id,
                    'name': enrollment.student.user.full_name
                },
                'status': attendance.status if attendance else None,
                'notes': attendance.notes if attendance else ''
            })
        
        # Calculate summary
        total_students = len(records)
        present = sum(1 for r in records if r['status'] == 'PRESENT')
        absent = sum(1 for r in records if r['status'] == 'ABSENT')
        late = sum(1 for r in records if r['status'] == 'LATE')
        excused = sum(1 for r in records if r['status'] == 'EXCUSED')
        
        return Response(
            StandardResponse.success(
                data={
                    'class': {
                        'id': str(class_instance.id),
                        'class_code': class_instance.class_code,
                        'course_name': class_instance.course.course_name,
                        'section': class_instance.section
                    },
                    'date': date,
                    'attendance_records': records,
                    'summary': {
                        'total_students': total_students,
                        'present': present,
                        'absent': absent,
                        'late': late,
                        'excused': excused
                    }
                }
            ),
            status=status.HTTP_200_OK
        )