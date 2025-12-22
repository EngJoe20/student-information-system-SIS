"""
Test suite for student and enrollment management.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date

from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Course, Class, Room
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
def admin_user(create_user):
    return create_user(
        username='admin',
        role='ADMIN',
        password='AdminPass123!'
    )


@pytest.fixture
def student_user(create_user):
    return create_user(
        username='student1',
        role='STUDENT',
        password='Student123!'
    )


@pytest.fixture
def other_student_user(create_user):
    return create_user(
        username='student2',
        role='STUDENT',
        password='Student123!'
    )


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authenticated_student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


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
def other_student(other_student_user):
    return Student.objects.create(
        user=other_student_user,
        student_id='STD002',
        date_of_birth='2000-02-02',
        gender='FEMALE',
        enrollment_date='2023-09-01'
    )


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
def room():
    return Room.objects.create(
        room_number='101',
        building='Main Hall',
        capacity=50,
        room_type='CLASSROOM'
    )


@pytest.fixture
def class_instance(course, room):
    return Class.objects.create(
        course=course,
        class_code='CS101-A',
        section='A',
        semester='FALL',
        academic_year=2024,
        max_capacity=30,
        room=room
    )


@pytest.fixture
def enrollment(student, class_instance):
    return Enrollment.objects.create(
        student=student,
        class_instance=class_instance,
        status='ENROLLED'
    )


# ------------------------------------------------------------------
# Tests: Student CRUD
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentCRUD:

    def test_list_students_as_admin(self, authenticated_admin_client, student):
        url = reverse('students-list')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Check results list inside data (handling pagination)
        assert len(response.data['data']['results']) >= 1

    def test_list_students_as_student(self, authenticated_student_client, student, other_student):
        """Student should only see their own profile."""
        url = reverse('students-list')
        response = authenticated_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # FIX 1: Count items in 'results', not the keys of the pagination dict
        assert len(response.data['data']['results']) == 1
        assert response.data['data']['results'][0]['student_id'] == student.student_id

    def test_create_student_as_admin(self, authenticated_admin_client):
        url = reverse('students-list')
        
        payload = {
            "user": {
                "username": "newstudent",
                "email": "new@test.com",
                "password": "securePass123!",
                "first_name": "New",
                "last_name": "Student",
                "phone_number": "1234567890"
            },
            "student_id": "STU999",
            "date_of_birth": "2001-01-01",
            "gender": "MALE",
            "address": "789 New St",
            "city": "New City",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA",
            "emergency_contact_name": "Mom",
            "emergency_contact_phone": "555-5555",
            "enrollment_date": "2024-01-01"
        }
        
        response = authenticated_admin_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Student.objects.filter(student_id="STU999").exists()

    def test_student_cannot_create_other_student(self, authenticated_student_client):
        url = reverse('students-list')
        payload = {"student_id": "STU999"}
        response = authenticated_student_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_student_with_active_enrollment(self, authenticated_admin_client, student, enrollment):
        url = reverse('students-detail', kwargs={'pk': student.id})
        response = authenticated_admin_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # FIX 2: Check top-level code, not nested under 'error'
        assert response.data['code'] == 'STUDENT_HAS_ACTIVE_ENROLLMENTS'

    def test_destroy_student_success(self, authenticated_admin_client, student):
        student.enrollments.all().delete()
        
        url = reverse('students-detail', kwargs={'pk': student.id})
        response = authenticated_admin_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not Student.objects.filter(id=student.id).exists()


# ------------------------------------------------------------------
# Tests: Student Actions
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentActions:

    def test_student_attendance_action(self, authenticated_student_client, student, enrollment):
        Attendance.objects.create(
            enrollment=enrollment,
            date=date.today(),
            status='PRESENT'
        )
        
        url = reverse('students-attendance', kwargs={'pk': student.id})
        response = authenticated_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['status'] == 'PRESENT'

    def test_student_transcript_action(self, authenticated_student_client, student, class_instance):
        Enrollment.objects.create(
            student=student,
            class_instance=class_instance,
            status='COMPLETED',
            final_grade='A',
            grade_points=4.00
        )
        
        url = reverse('students-transcript', kwargs={'pk': student.id})
        response = authenticated_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['gpa'] == 4.00


# ------------------------------------------------------------------
# Tests: Enrollments
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestEnrollmentCRUD:

    def test_create_enrollment_success(self, authenticated_student_client, student, class_instance):
        url = reverse('enrollments-list')
        payload = {
            "student": str(student.id),
            "class_instance": str(class_instance.id)
        }
        
        response = authenticated_student_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.filter(student=student, class_instance=class_instance).exists()

    def test_create_enrollment_for_other_forbidden(self, authenticated_student_client, student, other_student, class_instance):
        # FIX 3: Added 'student' fixture to arguments so logged-in user has a profile
        
        url = reverse('enrollments-list')
        payload = {
            "student": str(other_student.id), 
            "class_instance": str(class_instance.id)
        }
        
        response = authenticated_student_client.post(url, payload, format='json')
        
        # Check permissions logic (or business logic preventing it)
        # Assuming the view checks ownership first
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_drop_enrollment_success(self, authenticated_student_client, enrollment):
        url = reverse('enrollments-detail', kwargs={'pk': enrollment.id})
        response = authenticated_student_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        enrollment.refresh_from_db()
        assert enrollment.status == 'DROPPED'

    def test_drop_enrollment_not_owner(self, authenticated_student_client, other_student, class_instance):
        other_enrollment = Enrollment.objects.create(
            student=other_student,
            class_instance=class_instance,
            status='ENROLLED'
        )
        
        url = reverse('enrollments-detail', kwargs={'pk': other_enrollment.id})
        response = authenticated_student_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_drop_completed_enrollment_fails(self, authenticated_student_client, student, class_instance):
        enrollment = Enrollment.objects.create(
            student=student,
            class_instance=class_instance,
            status='COMPLETED'
        )
        
        url = reverse('enrollments-detail', kwargs={'pk': enrollment.id})
        response = authenticated_student_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST