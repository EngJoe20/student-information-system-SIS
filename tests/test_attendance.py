"""
Test suite for attendance management.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date

from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Course, Class
from attendance.models import Attendance


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        password = kwargs.pop('password', 'TestPass123!')
        user = User.objects.create_user(
            username=kwargs.get('username'),
            email=kwargs.get('email', f"{kwargs.get('username')}@test.com"),
            first_name='Test',
            last_name='User',
            role=kwargs.get('role', 'STUDENT')
        )
        user.set_password(password)
        user.save()
        return user
    return _create_user


@pytest.fixture
def instructor(create_user):
    return create_user(
        username='instructor1',
        role='INSTRUCTOR',
        password='Instructor123!'
    )


@pytest.fixture
def student_user(create_user):
    return create_user(
        username='student1',
        role='STUDENT',
        password='Student123!'
    )


@pytest.fixture
def authenticated_instructor_client(api_client, instructor):
    login_url = reverse('auth-login')
    response = api_client.post(
        login_url,
        {'username': instructor.username, 'password': 'Instructor123!'},
        format='json'
    )
    token = response.data['data']['access_token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def course():
    return Course.objects.create(
        course_code='CS101',
        course_name='Computer Science 101',
        description='Intro course',
        credits=3,
        department='CS'
    )


@pytest.fixture
def class_instance(course, instructor):
    return Class.objects.create(
        course=course,
        instructor=instructor,
        class_code='CS101-A',
        section='A',
        semester='FALL',
        academic_year=2025,
        max_capacity=30
    )


@pytest.fixture
def student(student_user):
    return Student.objects.create(
        user=student_user,
        student_id='STD001',
        date_of_birth='2000-01-01',
        gender='MALE',
        address='123 Main St',
        city='Cairo',
        state='Cairo',
        postal_code='12345',
        country='Egypt',
        emergency_contact_name='Father',
        emergency_contact_phone='01000000000',
        enrollment_date='2023-09-01'
    )


@pytest.fixture
def enrollment(student, class_instance):
    return Enrollment.objects.create(
        student=student,
        class_instance=class_instance
    )


@pytest.fixture
def attendance(enrollment, instructor):
    return Attendance.objects.create(
        enrollment=enrollment,
        date=date.today(),
        status='PRESENT',
        recorded_by=instructor
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestAttendanceCRUD:

    def test_create_attendance_as_instructor(
        self, authenticated_instructor_client, enrollment
    ):
        url = reverse('attendance-list')
        payload = {
            'enrollment': str(enrollment.id),
            'date': str(date.today()),
            'status': 'PRESENT',
            'notes': 'On time'
        }

        response = authenticated_instructor_client.post(
            url, payload, format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Attendance.objects.count() == 1
        assert response.data['data']['status'] == 'PRESENT'

    def test_update_attendance(
        self, authenticated_instructor_client, attendance
    ):
        url = reverse(
            'attendance-detail',
            kwargs={'pk': attendance.id}
        )
        payload = {'status': 'LATE'}

        response = authenticated_instructor_client.put(
            url, payload, format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        attendance.refresh_from_db()
        assert attendance.status == 'LATE'


@pytest.mark.django_db
class TestAttendancePermissions:

    def test_student_cannot_create_attendance(
        self, api_client, student_user, enrollment
    ):
        login_url = reverse('auth-login')
        token = api_client.post(
            login_url,
            {'username': student_user.username, 'password': 'Student123!'},
            format='json'
        ).data['data']['access_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('attendance-list')
        response = api_client.post(url, {}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestStudentAttendanceView:

    def test_student_view_own_attendance(
        self, api_client, student_user, student, attendance
    ):
        login_url = reverse('auth-login')
        token = api_client.post(
            login_url,
            {'username': student_user.username, 'password': 'Student123!'},
            format='json'
        ).data['data']['access_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse(
            'attendance-student-attendance',
            kwargs={'student_id': student.id}
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['attendance_summary']['present'] == 1


@pytest.mark.django_db
class TestClassAttendanceView:

    def test_class_attendance_as_instructor(
        self, authenticated_instructor_client, class_instance, attendance
    ):
        url = reverse(
            'attendance-class-attendance',
            kwargs={'class_id': class_instance.id}
        )

        response = authenticated_instructor_client.get(
            url, {'date': str(date.today())}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['summary']['present'] == 1

    def test_class_attendance_missing_date(
        self, authenticated_instructor_client, class_instance
    ):
        url = reverse(
            'attendance-class-attendance',
            kwargs={'class_id': class_instance.id}
        )

        response = authenticated_instructor_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
