
"""
Dashboard views for Admin, Student, and Instructor roles.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import User
from accounts.permissions import IsAdmin, IsStudent, IsInstructor
from accounts.permissions import IsAdmin
from students.models import Student, Enrollment
from courses.models import Course, Class
from attendance.models import Attendance
from grades.models import Grade
from notifications.models import Notification, Message
from core.utils import StandardResponse

bearer_security = [{'Bearer': []}]


class DashboardViewSet(viewsets.GenericViewSet):
    """ViewSet for dashboard statistics."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get Admin Dashboard",
        operation_description="Get comprehensive statistics for admin dashboard",
        security=bearer_security,
        responses={
            200: openapi.Response(
                description="Admin dashboard data",
                examples={
                    "application/json": {
                        "status": "success",
                        "data": {
                            "statistics": {
                                "total_students": 500,
                                "active_students": 480,
                                "total_courses": 150,
                                "active_classes": 200
                            }
                        }
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='admin', permission_classes=[IsAdmin])
    def admin_dashboard(self, request):
        """Get admin dashboard statistics."""
        # User statistics
        total_students = Student.objects.filter(
            academic_status='ACTIVE'
        ).count()
        total_instructors = User.objects.filter(
            role='INSTRUCTOR',
            is_active=True
        ).count()
        
        # Course statistics
        total_courses = Course.objects.filter(is_active=True).count()
        active_classes = Class.objects.filter(
            status='OPEN',
            academic_year=datetime.now().year
        ).count()
        
        # Enrollment trends
        current_year = datetime.now().year
        enrollment_trends = []

        for semester in ['FALL', 'SPRING', 'SUMMER']:
            count = Enrollment.objects.filter(
                class_instance__academic_year=current_year,
                class_instance__semester=semester,
                status='ENROLLED'
            ).count()

            enrollment_trends.append({
                'semester': semester,
                'academic_year': current_year,
                'enrollment_count': count
            })

        
        # Recent activities
        from core.models import AuditLog
        recent_activities = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
        activities = [
            {
                'action': activity.action,
                'description': f"{activity.user.full_name if activity.user else 'System'} {activity.action.lower()}d {activity.model_name}",
                'timestamp': activity.timestamp
            }
            for activity in recent_activities
        ]
        
        # Pending requests
        from notifications.models import StudentRequest
        pending_requests = StudentRequest.objects.filter(status='PENDING').count()
        
        # Attendance overview
        attendance_stats = Attendance.objects.filter(
            date__gte=datetime.now() - timedelta(days=30)
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
        )
        
        avg_attendance_rate = 0
        if attendance_stats['total'] > 0:
            avg_attendance_rate = (attendance_stats['present'] / attendance_stats['total'] * 100)
        
        # Average class size
        avg_class_size = Class.objects.filter(
            status='OPEN',
            academic_year=current_year
        ).aggregate(Avg('current_enrollment'))['current_enrollment__avg'] or 0
        
        data = {
            'statistics': {
                'total_students': total_students,
                'active_students': total_students,
                'total_courses': total_courses,
                'active_classes': active_classes,
                'total_instructors': total_instructors,
                'average_class_size': round(avg_class_size, 1)
            },
            'enrollment_trends': enrollment_trends,
            'recent_activities': activities,
            'pending_requests': pending_requests,
            'attendance_overview': {
                'average_attendance_rate': round(avg_attendance_rate, 1),
                'classes_below_threshold': 0
            }
        }
        
        return Response(
            StandardResponse.success(data=data),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Get Student Dashboard",
        operation_description="Get personalized dashboard for student",
        security=bearer_security
    )
    @action(detail=False, methods=['get'], url_path='student')
    def student_dashboard(self, request):
        """Get student dashboard."""
        user = request.user
        
        if user.role != 'STUDENT':
            return Response(
                StandardResponse.error(
                    message='Only students can access this dashboard',
                    code='INVALID_ROLE'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = user.student_profile
        
        # Current semester enrollments
        current_semester_enrollments = Enrollment.objects.filter(
            student=student,
            status='ENROLLED',
            class_obj__academic_year=datetime.now().year
        ).select_related('class_obj__course', 'class_obj__instructor')
        
        enrolled_classes = []
        total_credits = 0
        
        for enrollment in current_semester_enrollments:
            class_obj = enrollment.class_obj
            
            # Get current grade
            grades = Grade.objects.filter(enrollment=enrollment)
            current_grade = None
            if grades.exists():
                total_weight = sum(g.weight_percentage for g in grades)
                if total_weight > 0:
                    weighted_sum = sum(
                        (g.marks_obtained / g.total_marks * 100) * g.weight_percentage
                        for g in grades
                    )
                    current_grade = weighted_sum / total_weight
            
            enrolled_classes.append({
                'class_code': class_obj.class_code,
                'course_name': class_obj.course.course_name,
                'instructor_name': class_obj.instructor.full_name,
                'schedule': class_obj.schedule,
                'current_grade': f"{current_grade:.1f}%" if current_grade else None
            })
            
            total_credits += class_obj.course.credits
        
        # Calculate semester GPA
        semester_gpa = 0
        graded_enrollments = current_semester_enrollments.exclude(grade_points__isnull=True)
        if graded_enrollments.exists():
            semester_gpa = graded_enrollments.aggregate(
                Avg('grade_points')
            )['grade_points__avg'] or 0
        
        # Upcoming exams
        from courses.models import Exam
        upcoming_exams = Exam.objects.filter(
            class_obj__in=[e.class_obj for e in current_semester_enrollments],
            exam_date__gte=datetime.now()
        ).order_by('exam_date')[:5]
        
        exams = [
            {
                'course_name': exam.class_obj.course.course_name,
                'exam_type': exam.get_exam_type_display(),
                'exam_date': exam.exam_date,
                'room': f"{exam.room.building} - {exam.room.room_number}" if exam.room else 'TBA'
            }
            for exam in upcoming_exams
        ]
        
        # Recent grades
        recent_grades = Grade.objects.filter(
            enrollment__student=student
        ).select_related('enrollment__class_obj__course').order_by('-graded_date')[:5]
        
        grades_list = [
            {
                'course_name': grade.enrollment.class_obj.course.course_name,
                'assignment_name': grade.assignment_name,
                'grade': f"{(grade.marks_obtained / grade.total_marks * 100):.1f}%",
                'date': grade.graded_date
            }
            for grade in recent_grades
        ]
        
        # Attendance summary
        attendance_records = Attendance.objects.filter(
            enrollment__student=student,
            enrollment__status='ENROLLED'
        )
        total_attendance = attendance_records.count()
        present_count = attendance_records.filter(status='PRESENT').count()
        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        
        classes_at_risk = 0
        for enrollment in current_semester_enrollments:
            enr_attendance = Attendance.objects.filter(enrollment=enrollment)
            if enr_attendance.count() > 0:
                enr_rate = enr_attendance.filter(status='PRESENT').count() / enr_attendance.count() * 100
                if enr_rate < 75:
                    classes_at_risk += 1
        
        # Notifications and messages
        unread_notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        
        unread_messages = Message.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        
        data = {
            'student_profile': {
                'student_id': student.student_id,
                'name': user.full_name,
                'academic_status': student.get_academic_status_display(),
                'cumulative_gpa': float(student.gpa)
            },
            'current_semester': {
                'semester': 'FALL',
                'academic_year': datetime.now().year,
                'enrolled_courses': len(enrolled_classes),
                'total_credits': total_credits,
                'semester_gpa': float(semester_gpa)
            },
            'enrolled_classes': enrolled_classes,
            'upcoming_exams': exams,
            'recent_grades': grades_list,
            'attendance_summary': {
                'attendance_rate': round(attendance_rate, 1),
                'classes_at_risk': classes_at_risk
            },
            'unread_notifications': unread_notifications,
            'unread_messages': unread_messages
        }
        
        return Response(
            StandardResponse.success(data=data),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Get Instructor Dashboard",
        operation_description="Get dashboard for instructor with class overview",
        security=bearer_security
    )
    @action(detail=False, methods=['get'], url_path='instructor')
    def instructor_dashboard(self, request):
        """Get instructor dashboard."""
        user = request.user
        
        if user.role != 'INSTRUCTOR':
            return Response(
                StandardResponse.error(
                    message='Only instructors can access this dashboard',
                    code='INVALID_ROLE'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Current classes
        current_year = datetime.now().year
        my_classes = Class.objects.filter(
            instructor=user,
            academic_year=current_year,
            status='OPEN'
        ).select_related('course', 'room')
        
        classes_list = []
        total_students = 0
        
        for class_obj in my_classes:
            # Calculate average attendance
            class_attendance = Attendance.objects.filter(
                enrollment__class_obj=class_obj
            )
            total_att = class_attendance.count()
            present_att = class_attendance.filter(status='PRESENT').count()
            avg_attendance = (present_att / total_att * 100) if total_att > 0 else 0
            
            classes_list.append({
                'class_code': class_obj.class_code,
                'course_name': class_obj.course.course_name,
                'section': class_obj.section,
                'enrolled_students': class_obj.current_enrollment,
                'schedule': class_obj.schedule,
                'average_attendance': round(avg_attendance, 1)
            })
            
            total_students += class_obj.current_enrollment
        
        # Upcoming exams
        from courses.models import Exam
        upcoming_exams = Exam.objects.filter(
            class_obj__in=my_classes,
            exam_date__gte=datetime.now()
        ).order_by('exam_date')[:5]
        
        exams = [
            {
                'class_code': exam.class_obj.class_code,
                'exam_type': exam.get_exam_type_display(),
                'exam_date': exam.exam_date,
                'room': f"{exam.room.building} - {exam.room.room_number}" if exam.room else 'TBA'
            }
            for exam in upcoming_exams
        ]
        
        # Pending grading
        pending_grading = Enrollment.objects.filter(
            class_obj__in=my_classes,
            status='ENROLLED',
            grade__isnull=True
        ).count()
        
        # Recent activities
        from core.models import AuditLog
        recent_activities = AuditLog.objects.filter(
            user=user,
            model_name__in=['Grade', 'Attendance']
        ).order_by('-timestamp')[:10]
        
        activities = [
            {
                'action': activity.action,
                'description': f"{activity.action} in {activity.model_name}",
                'timestamp': activity.timestamp
            }
            for activity in recent_activities
        ]
        
        data = {
            'instructor_profile': {
                'name': user.full_name,
                'department': 'Computer Science'
            },
            'current_semester': {
                'semester': 'FALL',
                'academic_year': current_year,
                'total_classes': my_classes.count(),
                'total_students': total_students
            },
            'my_classes': classes_list,
            'upcoming_exams': exams,
            'pending_grading': pending_grading,
            'recent_activities': activities
        }
        
        return Response(
            StandardResponse.success(data=data),
            status=status.HTTP_200_OK
        )
