"""
Views for notifications, messaging, and student requests.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import HttpResponse
import json

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from notifications.models import Notification, Message, StudentRequest
from notifications.serializers import (
    NotificationSerializer, MessageSerializer, MessageCreateSerializer,
    MessageDetailSerializer, StudentRequestSerializer,
    StudentRequestCreateSerializer, StudentRequestUpdateSerializer,
    TranscriptRequestSerializer, ReportGenerationSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrRegistrar
from core.utils import StandardResponse
from core.reports import (
    TranscriptGenerator, AttendanceReportGenerator, GradeReportGenerator
)
from core.notifications import RequestNotificationTrigger

bearer_security = [{'Bearer': []}]


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notification management."""
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user."""
        return Notification.objects.filter(recipient=self.request.user)
    
    @swagger_auto_schema(
        operation_summary="List User Notifications",
        manual_parameters=[
            openapi.Parameter('is_read', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('notification_type', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        security=bearer_security
    )
    def list(self, request):
        """List user notifications with filters."""
        queryset = self.get_queryset()
        
        is_read = request.query_params.get('is_read')
        notification_type = request.query_params.get('notification_type')
        
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        unread_count = queryset.filter(is_read=False).count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                'unread_count': unread_count,
                'results': serializer.data
            }
            return self.get_paginated_response(response_data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data={
                'unread_count': unread_count,
                'results': serializer.data
            }),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Mark Notification as Read",
        security=bearer_security
    )
    @action(detail=True, methods=['put'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        return Response(
            StandardResponse.success(
                message='Notification marked as read',
                data={'id': str(notification.id), 'is_read': True}
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Mark All Notifications as Read",
        security=bearer_security
    )
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        
        return Response(
            StandardResponse.success(
                message='All notifications marked as read',
                data={'updated_count': updated_count}
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Delete Notification",
        security=bearer_security
    )
    def destroy(self, request, pk=None):
        """Delete notification."""
        notification = self.get_object()
        notification.delete()
        
        return Response(
            StandardResponse.success(message='Notification deleted successfully'),
            status=status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for internal messaging system."""
    
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get messages for current user."""
        user = self.request.user
        folder = self.request.query_params.get('folder', 'inbox')
        
        if folder == 'sent':
            return Message.objects.filter(sender=user)
        else:  # inbox
            return Message.objects.filter(recipient=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action == 'retrieve':
            return MessageDetailSerializer
        return MessageSerializer
    
    @swagger_auto_schema(
        operation_summary="List Messages",
        manual_parameters=[
            openapi.Parameter('folder', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                            description='inbox or sent'),
            openapi.Parameter('is_read', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        security=bearer_security
    )
    def list(self, request):
        """List messages with filters."""
        queryset = self.get_queryset()
        
        is_read = request.query_params.get('is_read')
        search = request.query_params.get('search')
        
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(body__icontains=search)
            )
        
        unread_count = Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                'unread_count': unread_count,
                'results': serializer.data
            }
            return self.get_paginated_response(response_data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data={
                'unread_count': unread_count,
                'results': serializer.data
            }),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Send Message",
        request_body=MessageCreateSerializer,
        security=bearer_security
    )
    def create(self, request):
        """Send new message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Message sent successfully',
                data=MessageSerializer(message).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Get Message Details",
        security=bearer_security
    )
    def retrieve(self, request, pk=None):
        """Get message details and mark as read."""
        message = self.get_object()
        
        # Mark as read if recipient
        if message.recipient == request.user and not message.is_read:
            message.is_read = True
            message.save()
        
        serializer = self.get_serializer(message)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Delete Message",
        security=bearer_security
    )
    def destroy(self, request, pk=None):
        """Delete message."""
        message = self.get_object()
        
        # Only sender or recipient can delete
        if message.sender != request.user and message.recipient != request.user:
            return Response(
                StandardResponse.error(
                    message='Permission denied',
                    code='PERMISSION_DENIED'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.delete()
        
        return Response(
            StandardResponse.success(message='Message deleted successfully'),
            status=status.HTTP_200_OK
        )


class StudentRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for student request management."""
    
    serializer_class = StudentRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get requests based on user role."""
        user = self.request.user
        
        if user.role in ['ADMIN', 'REGISTRAR']:
            return StudentRequest.objects.all()
        elif user.role == 'STUDENT':
            return StudentRequest.objects.filter(student__user=user)
        
        return StudentRequest.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentRequestUpdateSerializer
        return StudentRequestSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAdminOrRegistrar()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_summary="List Student Requests",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('request_type', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        security=bearer_security
    )
    def list(self, request):
        """List student requests with filters."""
        queryset = self.get_queryset()
        
        status_filter = request.query_params.get('status')
        request_type = request.query_params.get('request_type')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if request_type:
            queryset = queryset.filter(request_type=request_type)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            StandardResponse.success(data=serializer.data),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Submit Student Request",
        request_body=StudentRequestCreateSerializer,
        security=bearer_security
    )
    def create(self, request):
        """Submit new student request."""
        if request.user.role != 'STUDENT':
            return Response(
                StandardResponse.error(
                    message='Only students can submit requests',
                    code='INVALID_ROLE'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_request = serializer.save()
        
        return Response(
            StandardResponse.success(
                message='Request submitted successfully',
                data=StudentRequestSerializer(student_request).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Update Request Status",
        request_body=StudentRequestUpdateSerializer,
        security=bearer_security
    )
    def update(self, request, pk=None):
        """Update student request status."""
        student_request = self.get_object()
        serializer = self.get_serializer(student_request, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Send notification to student
        RequestNotificationTrigger.on_request_status_changed(student_request)
        
        return Response(
            StandardResponse.success(
                message='Request updated successfully',
                data=StudentRequestSerializer(student_request).data
            ),
            status=status.HTTP_200_OK
        )


class ReportViewSet(viewsets.GenericViewSet):
    """ViewSet for report generation."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Generate Student Transcript",
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, type=openapi.TYPE_STRING),
            openapi.Parameter('format', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                            description='pdf or json'),
        ],
        security=bearer_security
    )
    @action(detail=False, methods=['get'], url_path='transcript/(?P<student_id>[^/.]+)')
    def transcript(self, request, student_id=None):
        """Generate student transcript."""
        from students.models import Student
        
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
        
        # Permission check
        user = request.user
        if user.role == 'STUDENT' and student.user != user:
            return Response(
                StandardResponse.error(
                    message='Permission denied',
                    code='PERMISSION_DENIED'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        format_type = request.query_params.get('format', 'pdf')
        
        if format_type == 'pdf':
            buffer = TranscriptGenerator.generate_pdf(student)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="transcript_{student.student_id}.pdf"'
            return response
        else:
            data = TranscriptGenerator.generate_json(student)
            return Response(
                StandardResponse.success(data=data),
                status=status.HTTP_200_OK
            )
    
    @swagger_auto_schema(
        operation_summary="Generate Attendance Report",
        request_body=ReportGenerationSerializer,
        security=bearer_security
    )
    @action(detail=False, methods=['post'], url_path='attendance')
    def attendance_report(self, request):
        """Generate attendance report."""
        from attendance.models import Attendance
        from students.models import Student
        
        serializer = ReportGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_id = serializer.validated_data.get('student_id')
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        format_type = serializer.validated_data.get('format', 'pdf')
        
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
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            enrollment__student=student
        )
        
        if start_date:
            attendance_records = attendance_records.filter(date__gte=start_date)
        if end_date:
            attendance_records = attendance_records.filter(date__lte=end_date)
        
        # Calculate statistics
        total = attendance_records.count()
        present = attendance_records.filter(status='PRESENT').count()
        absent = attendance_records.filter(status='ABSENT').count()
        late = attendance_records.filter(status='LATE').count()
        excused = attendance_records.filter(status='EXCUSED').count()
        
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        report_data = {
            'period': {
                'start_date': start_date.strftime('%m/%d/%Y') if start_date else 'N/A',
                'end_date': end_date.strftime('%m/%d/%Y') if end_date else 'N/A'
            },
            'summary': {
                'total_days': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'attendance_percentage': attendance_percentage
            },
            'details': [
                {
                    'date': record.date.strftime('%m/%d/%Y'),
                    'course_name': record.enrollment.class_obj.course.course_name,
                    'status': record.get_status_display()
                }
                for record in attendance_records
            ]
        }
        
        if format_type == 'pdf':
            buffer = AttendanceReportGenerator.generate_pdf(report_data)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="attendance_{student.student_id}.pdf"'
            return response
        elif format_type == 'csv':
            buffer = AttendanceReportGenerator.generate_csv(report_data)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="attendance_{student.student_id}.csv"'
            return response
        else:
            return Response(
                StandardResponse.success(data=report_data),
                status=status.HTTP_200_OK
            )
    
    @swagger_auto_schema(
        operation_summary="Generate Grade Report",
        request_body=ReportGenerationSerializer,
        security=bearer_security
    )
    @action(detail=False, methods=['post'], url_path='grades')
    def grade_report(self, request):
        """Generate grade report for a class."""
        from courses.models import Class
        from students.models import Enrollment
        
        serializer = ReportGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        class_id = serializer.validated_data.get('class_id')
        format_type = serializer.validated_data.get('format', 'pdf')
        
        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response(
                StandardResponse.error(
                    message='Class not found',
                    code='RESOURCE_NOT_FOUND'
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get enrollments
        enrollments = Enrollment.objects.filter(class_obj=class_obj)
        
        # Calculate statistics
        total_students = enrollments.count()
        graded_students = enrollments.exclude(grade__isnull=True)
        
        if graded_students.exists():
            from django.db.models import Avg
            avg_grade = graded_students.aggregate(Avg('grade_points'))['grade_points__avg'] or 0
        else:
            avg_grade = 0
        
        student_grades = [
            {
                'student_id': enrollment.student.student_id,
                'student_name': enrollment.student.user.full_name,
                'final_grade': enrollment.grade,
                'grade_points': float(enrollment.grade_points) if enrollment.grade_points else None
            }
            for enrollment in enrollments
        ]
        
        report_data = {
            'class': {
                'class_code': class_obj.class_code,
                'course_name': class_obj.course.course_name,
                'section': class_obj.section,
                'instructor_name': class_obj.instructor.full_name,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year
            },
            'statistics': {
                'total_students': total_students,
                'average_grade': avg_grade * 25  # Convert to percentage
            },
            'student_grades': student_grades
        }
        
        if format_type == 'pdf':
            buffer = GradeReportGenerator.generate_pdf(report_data)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="grades_{class_obj.class_code}.pdf"'
            return response
        elif format_type == 'csv':
            buffer = GradeReportGenerator.generate_csv(report_data)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="grades_{class_obj.class_code}.csv"'
            return response
        else:
            return Response(
                StandardResponse.success(data=report_data),
                status=status.HTTP_200_OK
            )