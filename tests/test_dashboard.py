import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta
from faker import Faker

from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Course, Class
from attendance.models import Attendance
from grades.models import Grade
from notifications.models import Notification, Message
from core.models import AuditLog
from notifications.models import StudentRequest

fake = Faker()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    counter = 0
    def _create_user(**kwargs):
        nonlocal counter
        counter += 1
        defaults = {
            'username': kwargs.get('username', f'user{counter}'),
            'email': kwargs.get('email', f'user{counter}@example.com'),
            'first_name': kwargs.get('first_name', fake.first_name()),
            'last_name': kwargs.get('last_name', fake.last_name()),
            'role': kwargs.get('role', 'STUDENT'),
            'is_active': kwargs.get('is_active', True),
        }
        password = kwargs.get('password', 'TestPass123!')
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return _create_user


@pytest.mark.django_db
class TestDashboardViewSet:

    def authenticate(self, client, user, password='TestPass123!'):
        client.force_authenticate(user=user)

    def test_admin_dashboard_success(self, api_client, create_user):
        admin = create_user(username='admin', role='ADMIN')
        self.authenticate(api_client, admin)

        # إنشاء طلاب مع enrollment_date إلزامي وتاريخ ميلاد عشوائي
        for i in range(3):
            student_user = create_user(username=f'student{i}', role='STUDENT')
            Student.objects.create(
                user=student_user,
                academic_status='ACTIVE',
                student_id=f'S{i}',
                enrollment_date=fake.date_between(start_date='-4y', end_date='today'),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
                gpa=fake.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0, max_value=4)
            )
        # Instructors
        for i in range(2):
            create_user(username=f'instructor{i}', role='INSTRUCTOR')

        course = Course.objects.create(course_name='Test Course', is_active=True, credits=3)
        Class.objects.create(
            class_code='C101',
            course=course,
            instructor=User.objects.filter(role='INSTRUCTOR').first(),
            academic_year=datetime.now().year,
            status='OPEN',
            current_enrollment=10,
            schedule='MWF 9-10AM',
            section='A',
            max_capacity=30
        )
        AuditLog.objects.create(action='Created', model_name='Course', timestamp=datetime.now())
        StudentRequest.objects.create(status='PENDING')
        Attendance.objects.create(date=datetime.now(), status='PRESENT')

        url = reverse('dashboard-admin-dashboard')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert 'statistics' in data
        assert data['statistics']['total_students'] == 3
        assert data['statistics']['total_instructors'] == 2
        assert data['statistics']['total_courses'] == 1
        assert data['statistics']['active_classes'] == 1
        assert 'enrollment_trends' in data
        assert 'recent_activities' in data
        assert 'pending_requests' in data
        assert 'attendance_overview' in data

    def test_student_dashboard_success(self, api_client, create_user):
        student_user = create_user(username='stud1', role='STUDENT')
        student_profile = Student.objects.create(
            user=student_user,
            academic_status='ACTIVE',
            student_id='S100',
            enrollment_date=fake.date_between(start_date='-4y', end_date='today'),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
            gpa=3.5
        )
        self.authenticate(api_client, student_user)

        course = Course.objects.create(course_name='Math', credits=3)
        instructor = create_user(username='instr1', role='INSTRUCTOR')
        class_obj = Class.objects.create(
            class_code='MATH101',
            course=course,
            instructor=instructor,
            academic_year=datetime.now().year,
            status='OPEN',
            current_enrollment=5,
            schedule='TTh 10-11',
            section='B',
            max_capacity=30
        )
        enrollment = Enrollment.objects.create(student=student_profile, class_obj=class_obj, status='ENROLLED', grade_points=3.7)

        Grade.objects.create(
            enrollment=enrollment,
            assignment_name='Midterm',
            marks_obtained=85,
            total_marks=100,
            weight_percentage=50,
            graded_date=datetime.now()
        )
        Grade.objects.create(
            enrollment=enrollment,
            assignment_name='Final',
            marks_obtained=90,
            total_marks=100,
            weight_percentage=50,
            graded_date=datetime.now()
        )

        from courses.models import Exam
        Exam.objects.create(
            class_obj=class_obj,
            exam_type='MIDTERM',
            exam_date=datetime.now() + timedelta(days=5),
            room=None
        )

        Attendance.objects.create(enrollment=enrollment, status='PRESENT')
        Attendance.objects.create(enrollment=enrollment, status='ABSENT')

        Notification.objects.create(recipient=student_user, is_read=False)
        Message.objects.create(recipient=student_user, is_read=False)

        url = reverse('dashboard-student-dashboard')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert data['student_profile']['student_id'] == 'S100'
        assert len(data['enrolled_classes']) == 1
        assert len(data['upcoming_exams']) >= 1
        assert len(data['recent_grades']) >= 1
        assert data['attendance_summary']['attendance_rate'] >= 0
        assert data['unread_notifications'] == 1
        assert data['unread_messages'] == 1

    def test_student_dashboard_wrong_role_forbidden(self, api_client, create_user):
        user = create_user(username='not_student', role='INSTRUCTOR')
        self.authenticate(api_client, user)

        url = reverse('dashboard-student-dashboard')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_instructor_dashboard_success(self, api_client, create_user):
        instructor_user = create_user(username='instructor1', role='INSTRUCTOR')
        self.authenticate(api_client, instructor_user)

        course = Course.objects.create(course_name='Physics', credits=4)
        class_obj = Class.objects.create(
            class_code='PHY101',
            course=course,
            instructor=instructor_user,
            academic_year=datetime.now().year,
            status='OPEN',
            current_enrollment=7,
            schedule='MWF 1-2PM',
            section='C',
            max_capacity=30
        )

        student_user = create_user(username='studentX', role='STUDENT')
        student_profile = Student.objects.create(
            user=student_user,
            academic_status='ACTIVE',
            student_id='S200',
            enrollment_date=fake.date_between(start_date='-4y', end_date='today'),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
            gpa=0.0
        )
        enrollment = Enrollment.objects.create(student=student_profile, class_obj=class_obj, status='ENROLLED')

        Attendance.objects.create(enrollment=enrollment, status='PRESENT')

        AuditLog.objects.create(user=instructor_user, action='Updated', model_name='Grade', timestamp=datetime.now())

        url = reverse('dashboard-instructor-dashboard')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert data['instructor_profile']['name'] == instructor_user.full_name
        assert data['current_semester']['total_classes'] >= 1
        assert 'my_classes' in data
        assert 'upcoming_exams' in data
        assert 'pending_grading' in data
        assert 'recent_activities' in data

    def test_instructor_dashboard_wrong_role_forbidden(self, api_client, create_user):
        user = create_user(username='not_instructor', role='STUDENT')
        self.authenticate(api_client, user)

        url = reverse('dashboard-instructor-dashboard')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
