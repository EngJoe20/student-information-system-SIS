"""
Test suite for Course, Class, Room, and Exam management.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from django.utils import timezone

from accounts.models import User
from courses.models import Course, Class, Room, Exam

fake = Faker()


# ==================================================
# Fixtures
# ==================================================

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        defaults = {
            'username': kwargs.get('username', fake.unique.user_name()),
            'email': kwargs.get('email', fake.unique.email()),
            'first_name': 'Test',
            'last_name': 'User',
            'role': kwargs.get('role', 'STUDENT'),
        }
        password = kwargs.get('password', 'TestPass123!')
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return _create_user


@pytest.fixture
def authenticate(api_client, create_user):
    def _authenticate(role='ADMIN'):
        user = create_user(role=role)
        response = api_client.post(
            reverse('auth-login'),
            {'username': user.username, 'password': 'TestPass123!'},
            format='json'
        )
        token = response.data['data']['access_token']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return user
    return _authenticate


# ==================================================
# Course Tests
# ==================================================

@pytest.mark.django_db
class TestCourseManagement:

    def test_admin_can_create_course(self, api_client, authenticate):
        authenticate(role='ADMIN')

        response = api_client.post(
            reverse('courses-list'),
            {
                'course_code': 'CS101',
                'course_name': 'Intro to CS',
                'description': 'Basics',
                'credits': 3,
                'department': 'CS'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Course.objects.filter(course_code='CS101').exists()

    def test_list_courses(self, api_client, authenticate):
        authenticate()

        Course.objects.create(
            course_code='CS102',
            course_name='Algorithms',
            description='Algo course',
            credits=3,
            department='CS'
        )

        response = api_client.get(reverse('courses-list'))

        assert response.status_code == status.HTTP_200_OK

        # works with wrapped or plain responses
        data = response.data.get('data', response.data)
        assert len(data) >= 1

    def test_course_detail_returns_course(self, api_client, authenticate):
        authenticate()

        course = Course.objects.create(
            course_code='CS103',
            course_name='Databases',
            description='DB',
            credits=3,
            department='CS'
        )

        response = api_client.get(
            reverse('courses-detail', kwargs={'pk': course.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['course_code'] == 'CS103'

    def test_delete_course_with_active_class_fails(self, api_client, authenticate):
        authenticate(role='ADMIN')

        course = Course.objects.create(
            course_code='CS104',
            course_name='OS',
            description='OS',
            credits=3,
            department='CS'
        )

        Class.objects.create(
            course=course,
            class_code='CS104-A',
            section='A',
            semester='FALL',
            academic_year=2025,
            max_capacity=30
        )

        response = api_client.delete(
            reverse('courses-detail', kwargs={'pk': course.id})
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ==================================================
# Class Tests
# ==================================================

@pytest.mark.django_db
class TestClassManagement:

    def test_registrar_can_create_class(self, api_client, authenticate, create_user):
        authenticate(role='REGISTRAR')

        instructor = create_user(role='INSTRUCTOR')

        course = Course.objects.create(
            course_code='CS201',
            course_name='AI',
            description='AI course',
            credits=3,
            department='CS'
        )

        room = Room.objects.create(
            room_number='A101',
            building='Main',
            capacity=40,
            room_type='CLASSROOM'
        )

        response = api_client.post(
            reverse('classes-list'),
            {
                'course': course.id,
                'instructor': instructor.id,
                'class_code': 'CS201-A',
                'section': 'A',
                'semester': 'SPRING',
                'academic_year': 2025,
                'max_capacity': 30,
                'room': room.id,
                'schedule': [                       # 🔥 REQUIRED
                    {
                        'day': 'MONDAY',
                        'start_time': '10:00',
                        'end_time': '12:00'
                    }
                ]
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_class_list_filter_by_semester(self, api_client, authenticate):
        authenticate()

        response = api_client.get(
            reverse('classes-list'),
            {'semester': 'SPRING'}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_class_available_seats_property(self, db):
        course = Course.objects.create(
            course_code='CS202',
            course_name='ML',
            description='ML',
            credits=3,
            department='CS'
        )

        class_instance = Class.objects.create(
            course=course,
            class_code='CS202-A',
            section='A',
            semester='FALL',
            academic_year=2025,
            max_capacity=10,
            current_enrollment=6
        )

        assert class_instance.available_seats == 4


# ==================================================
# Room Tests
# ==================================================

@pytest.mark.django_db
class TestRoomManagement:

    def test_admin_can_create_room(self, api_client, authenticate):
        authenticate(role='ADMIN')

        response = api_client.post(
            reverse('rooms-list'),
            {
                'room_number': 'B101',
                'building': 'Main',
                'capacity': 50,
                'room_type': 'LECTURE_HALL'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Room.objects.filter(room_number='B101').exists()

    def test_list_available_rooms(self, api_client, authenticate):
        authenticate()

        Room.objects.create(
            room_number='C202',
            building='Science',
            capacity=40,
            room_type='CLASSROOM',
            is_available=True
        )

        response = api_client.get(reverse('rooms-available'))

        assert response.status_code == status.HTTP_200_OK


# ==================================================
# Exam Tests
# ==================================================

@pytest.mark.django_db
class TestExamManagement:

    def test_registrar_can_create_exam(self, api_client, authenticate):
        authenticate(role='REGISTRAR')

        course = Course.objects.create(
            course_code='CS301',
            course_name='Networks',
            description='Networks',
            credits=3,
            department='CS'
        )

        class_instance = Class.objects.create(
            course=course,
            class_code='CS301-A',
            section='A',
            semester='SPRING',
            academic_year=2025,
            max_capacity=30
        )

        room = Room.objects.create(
            room_number='D303',
            building='Engineering',
            capacity=60,
            room_type='CLASSROOM'
        )

        response = api_client.post(
            reverse('exams-list'),
            {
                'class_instance': class_instance.id,
                'exam_type': 'FINAL',
                'exam_date': timezone.now().isoformat(),
                'duration_minutes': 120,
                'room': room.id,
                'total_marks': 100
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Exam.objects.count() == 1

    def test_list_exams(self, api_client, authenticate):
        authenticate()

        response = api_client.get(reverse('exams-list'))

        assert response.status_code == status.HTTP_200_OK
