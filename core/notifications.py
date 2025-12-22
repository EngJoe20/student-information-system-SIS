"""
Notification triggers and email/SMS integration.
"""
from django.conf import settings
from notifications.models import Notification
from core.utils import send_email_notification


class NotificationService:
    """Service for creating and sending notifications."""
    
    @staticmethod
    def create_notification(recipient, notification_type, title, message, 
                          priority='MEDIUM', related_object=None):
        """Create a notification."""
        notification_data = {
            'recipient': recipient,
            'notification_type': notification_type,
            'title': title,
            'message': message,
            'priority': priority
        }
        
        if related_object:
            notification_data['related_object_type'] = related_object.__class__.__name__
            notification_data['related_object_id'] = related_object.id
        
        return Notification.objects.create(**notification_data)
    
    @staticmethod
    def send_email(user, subject, template_name, context):
        """Send email notification."""
        return send_email_notification(
            to_email=user.email,
            subject=subject,
            template_name=template_name,
            context=context
        )


class GradeNotificationTrigger:
    """Trigger notifications when grades are posted."""
    
    @staticmethod
    def on_grade_posted(grade):
        """Send notification when grade is posted."""
        enrollment = grade.enrollment
        student = enrollment.student
        user = student.user
        
        # Create in-app notification
        NotificationService.create_notification(
            recipient=user,
            notification_type='GRADE',
            title='New Grade Posted',
            message=f"A new grade has been posted for {enrollment.class_obj.course.course_name}",
            priority='MEDIUM',
            related_object=grade
        )
        
        # Send email
        NotificationService.send_email(
            user=user,
            subject=f'New Grade Posted - {enrollment.class_obj.course.course_name}',
            template_name='grade_notification.html',
            context={
                'student': student,
                'course': enrollment.class_obj.course,
                'assignment': grade.assignment_name,
                'score': grade.marks_obtained,
                'total': grade.total_marks,
                'percentage': (grade.marks_obtained / grade.total_marks * 100)
            }
        )
    
    @staticmethod
    def on_final_grade_posted(enrollment):
        """Send notification when final grade is posted."""
        student = enrollment.student
        user = student.user
        
        # Create in-app notification
        NotificationService.create_notification(
            recipient=user,
            notification_type='GRADE',
            title='Final Grade Posted',
            message=f"Your final grade for {enrollment.class_obj.course.course_name} has been posted: {enrollment.grade}",
            priority='HIGH',
            related_object=enrollment
        )
        
        # Send email
        NotificationService.send_email(
            user=user,
            subject=f'Final Grade Posted - {enrollment.class_obj.course.course_name}',
            template_name='final_grade_notification.html',
            context={
                'student': student,
                'course': enrollment.class_obj.course,
                'grade': enrollment.grade,
                'grade_points': enrollment.grade_points
            }
        )


class AttendanceNotificationTrigger:
    """Trigger notifications for attendance alerts."""
    
    @staticmethod
    def check_attendance_threshold(enrollment):
        """Check if attendance is below threshold and send alert."""
        from attendance.models import Attendance
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(enrollment=enrollment)
        total = attendance_records.count()
        
        if total < 5:  # Need minimum records
            return
        
        present = attendance_records.filter(status='PRESENT').count()
        percentage = (present / total * 100) if total > 0 else 0
        
        # Alert if below 75%
        if percentage < 75:
            student = enrollment.student
            user = student.user
            
            # Create notification
            NotificationService.create_notification(
                recipient=user,
                notification_type='ATTENDANCE',
                title='Low Attendance Alert',
                message=f"Your attendance in {enrollment.class_obj.course.course_name} is {percentage:.1f}%. Minimum required is 75%.",
                priority='HIGH',
                related_object=enrollment
            )
            
            # Send email
            NotificationService.send_email(
                user=user,
                subject=f'Attendance Alert - {enrollment.class_obj.course.course_name}',
                template_name='attendance_alert.html',
                context={
                    'student': student,
                    'course': enrollment.class_obj.course,
                    'attendance_percentage': percentage,
                    'threshold': 75
                }
            )


class EnrollmentNotificationTrigger:
    """Trigger notifications for enrollment events."""
    
    @staticmethod
    def on_enrollment_confirmed(enrollment):
        """Send notification when enrollment is confirmed."""
        student = enrollment.student
        user = student.user
        
        # Create notification
        NotificationService.create_notification(
            recipient=user,
            notification_type='ENROLLMENT',
            title='Enrollment Confirmed',
            message=f"You have been successfully enrolled in {enrollment.class_obj.course.course_name}",
            priority='MEDIUM',
            related_object=enrollment
        )
        
        # Send email
        NotificationService.send_email(
            user=user,
            subject=f'Enrollment Confirmation - {enrollment.class_obj.course.course_name}',
            template_name='enrollment_confirmation.html',
            context={
                'student': student,
                'course': enrollment.class_obj.course,
                'class': enrollment.class_obj,
                'enrollment_date': enrollment.enrollment_date
            }
        )
    
    @staticmethod
    def on_enrollment_dropped(enrollment):
        """Send notification when enrollment is dropped."""
        student = enrollment.student
        user = student.user
        
        # Create notification
        NotificationService.create_notification(
            recipient=user,
            notification_type='ENROLLMENT',
            title='Course Dropped',
            message=f"You have dropped {enrollment.class_obj.course.course_name}",
            priority='MEDIUM',
            related_object=enrollment
        )
        
        # Send email
        NotificationService.send_email(
            user=user,
            subject=f'Course Dropped - {enrollment.class_obj.course.course_name}',
            template_name='enrollment_dropped.html',
            context={
                'student': student,
                'course': enrollment.class_obj.course,
                'dropped_date': enrollment.updated_at
            }
        )


class RequestNotificationTrigger:
    """Trigger notifications for student request updates."""
    
    @staticmethod
    def on_request_status_changed(request):
        """Send notification when request status changes."""
        student = request.student
        user = student.user
        
        # Create notification
        NotificationService.create_notification(
            recipient=user,
            notification_type='SYSTEM',
            title='Request Status Updated',
            message=f"Your {request.get_request_type_display()} request status has been updated to {request.get_status_display()}",
            priority='MEDIUM',
            related_object=request
        )
        
        # Send email
        NotificationService.send_email(
            user=user,
            subject=f'Request Status Update - {request.get_request_type_display()}',
            template_name='request_status_update.html',
            context={
                'student': student,
                'request': request,
                'status': request.get_status_display(),
                'response': request.response
            }
        )


class SystemNotificationTrigger:
    """Trigger system-wide notifications."""
    
    @staticmethod
    def broadcast_announcement(users, title, message, priority='MEDIUM'):
        """Send announcement to multiple users."""
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    recipient=user,
                    notification_type='ANNOUNCEMENT',
                    title=title,
                    message=message,
                    priority=priority
                )
            )
        
        Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def send_exam_reminder(class_obj, exam):
        """Send exam reminder to all students in class."""
        from students.models import Enrollment
        
        enrollments = Enrollment.objects.filter(
            class_obj=class_obj,
            status='ENROLLED'
        ).select_related('student__user')
        
        for enrollment in enrollments:
            user = enrollment.student.user
            
            # Create notification
            NotificationService.create_notification(
                recipient=user,
                notification_type='SYSTEM',
                title='Exam Reminder',
                message=f"Reminder: {exam.get_exam_type_display()} for {class_obj.course.course_name} on {exam.exam_date.strftime('%m/%d/%Y %H:%M')}",
                priority='HIGH',
                related_object=exam
            )
            
            # Send email
            NotificationService.send_email(
                user=user,
                subject=f'Exam Reminder - {class_obj.course.course_name}',
                template_name='exam_reminder.html',
                context={
                    'student': enrollment.student,
                    'course': class_obj.course,
                    'exam': exam,
                    'exam_date': exam.exam_date
                }
            )