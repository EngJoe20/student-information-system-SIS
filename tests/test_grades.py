"""
Test suite for grade management.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Course, Class, Room, Exam
from grades.models import Grade


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
    return create_user(username='instructor1', role='INSTRUCTOR')

@pytest.fixture
def other_instructor(create_user):
    return create_user(username='instructor2', role='INSTRUCTOR')

@pytest.fixture
def student_user(create_user):
    return create_user(username='student1', role='STUDENT')

@pytest.fixture
def student_profile(student_user):
    return Student.objects.create(
        user=student_user,
        student_id='STU001',
        date_of_birth='2000-01-01',
        gender='MALE',
        enrollment_date='2025-01-01'
    )

@pytest.fixture
def course():
    return Course.objects.create(
        course_code='CS101',
        course_name='Computer Science 101',
        description='Intro',
        credits=3,
        department='CS'
    )

@pytest.fixture
def room():
    return Room.objects.create(
        room_number='101',
        building='Main',
        capacity=30,
        room_type='CLASSROOM'
    )

@pytest.fixture
def class_instance(course, instructor, room):
    return Class.objects.create(
        course=course,
        instructor=instructor,
        class_code='CS101-A',
        section='A',
        semester='FALL',
        academic_year=2025,
        max_capacity=30,
        room=room
    )

@pytest.fixture
def enrollment(student_profile, class_instance):
    return Enrollment.objects.create(
        student=student_profile,
        class_instance=class_instance,
        status='ENROLLED'
    )

@pytest.fixture
def exam(class_instance, room):
    from django.utils import timezone
    return Exam.objects.create(
        class_instance=class_instance,
        exam_type='MIDTERM',
        exam_date=timezone.now(),
        duration_minutes=60,
        room=room,
        total_marks=100.00
    )

@pytest.fixture
def grade(enrollment, instructor, exam):
    return Grade.objects.create(
        enrollment=enrollment,
        exam=exam,
        assignment_name="Midterm Exam",
        marks_obtained=85.00,
        total_marks=100.00,
        weight_percentage=30.00,
        graded_by=instructor
    )

@pytest.fixture
def auth_instructor_client(api_client, instructor):
    api_client.force_authenticate(user=instructor)
    return api_client

@pytest.fixture
def auth_student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


# ------------------------------------------------------------------
# Tests: Grade CRUD
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestGradeCRUD:

    def test_create_grade_as_instructor(self, auth_instructor_client, enrollment, exam):
        # Attempt both singular and plural URL names to be robust
        try:
            url = reverse('grades-list')
        except:
            url = reverse('grade-list')

        data = {
            "enrollment": str(enrollment.id),
            "exam": str(exam.id),
            "assignment_name": "Final Project",
            "marks_obtained": "90.00",
            "total_marks": "100.00",
            "weight_percentage": "40.00",
            "comments": "Excellent work"
        }
        
        response = auth_instructor_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Grade.objects.count() == 1
        assert Grade.objects.first().marks_obtained == Decimal('90.00')

    def test_instructor_cannot_grade_other_class(self, api_client, other_instructor, enrollment, exam):
        api_client.force_authenticate(user=other_instructor)
        try:
            url = reverse('grades-list')
        except:
            url = reverse('grade-list')
            
        data = {
            "enrollment": str(enrollment.id),
            "assignment_name": "Test",
            "marks_obtained": "50.00",
            "total_marks": "100.00",
            "weight_percentage": "10.00"
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_grade(self, auth_instructor_client, grade):
        try:
            url = reverse('grades-detail', kwargs={'pk': grade.id})
        except:
            url = reverse('grade-detail', kwargs={'pk': grade.id})
            
        data = {"marks_obtained": "95.00"}
        
        response = auth_instructor_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        grade.refresh_from_db()
        assert grade.marks_obtained == Decimal('95.00')

    def test_student_cannot_create_grade(self, auth_student_client, enrollment):
        try:
            url = reverse('grades-list')
        except:
            url = reverse('grade-list')
            
        data = {"assignment_name": "Hack"}
        response = auth_student_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ------------------------------------------------------------------
# Tests: Student Grade View
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentGradeView:

    def test_student_view_own_grades(self, auth_student_client, student_profile, grade):
        try:
            url = reverse('grades-student-grades', kwargs={'student_id': student_profile.id})
        except:
            url = reverse('grade-student-grades', kwargs={'student_id': student_profile.id})
            
        response = auth_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert data['student']['student_id'] == student_profile.student_id
        assert len(data['courses']) == 1
        assert data['courses'][0]['grades'][0]['marks_obtained'] == '85.00'

    def test_student_cannot_view_others_grades(self, auth_student_client, create_user):
        other_student = Student.objects.create(
            user=create_user(username='other', role='STUDENT'),
            student_id='STU002',
            date_of_birth='2000-01-01',
            gender='FEMALE',
            enrollment_date='2025-01-01'
        )
        
        try:
            url = reverse('grades-student-grades', kwargs={'student_id': other_student.id})
        except:
            url = reverse('grade-student-grades', kwargs={'student_id': other_student.id})
            
        response = auth_student_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ------------------------------------------------------------------
# Tests: Finalize Grade
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestFinalizeGrade:

    def test_finalize_grade_success(self, auth_instructor_client, enrollment):
        try:
            url = reverse('grades-finalize-grade', kwargs={'enrollment_id': enrollment.id})
        except:
            url = reverse('grade-finalize-grade', kwargs={'enrollment_id': enrollment.id})
            
        data = {"final_grade": "A"}
        
        response = auth_instructor_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        enrollment.refresh_from_db()
        assert enrollment.grade == 'A'
        assert enrollment.status == 'COMPLETED'
        assert enrollment.grade_points == Decimal('4.00')

    def test_finalize_grade_permission_denied(self, api_client, other_instructor, enrollment):
        api_client.force_authenticate(user=other_instructor)
        
        try:
            url = reverse('grades-finalize-grade', kwargs={'enrollment_id': enrollment.id})
        except:
            url = reverse('grade-finalize-grade', kwargs={'enrollment_id': enrollment.id})
            
        response = api_client.post(url, {"final_grade": "A"}, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ------------------------------------------------------------------
# Tests: Class Statistics
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestClassStatistics:

    def test_class_statistics_success(self, auth_instructor_client, class_instance, grade):
        try:
            url = reverse('grades-class-statistics', kwargs={'class_id': class_instance.id})
        except:
            url = reverse('grade-class-statistics', kwargs={'class_id': class_instance.id})
            
        # Setup completed enrollment for stats
        grade.enrollment.status = 'COMPLETED'
        grade.enrollment.grade = 'B'
        grade.enrollment.grade_points = 3.00
        grade.enrollment.save()
        
        response = auth_instructor_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        stats = response.data['data']['statistics']
        assert stats['total_students'] == 1
        assert stats['average_grade'] == 3.00
        assert stats['grade_distribution']['B'] == 1