import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Exam, Class
from grades.models import Grade


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        user = User.objects.create_user(
            username=kwargs.get('username', 'user'),
            email=kwargs.get('email', 'user@example.com'),
            password=kwargs.get('password', 'TestPass123!'),
            role=kwargs.get('role', 'STUDENT'),
            first_name=kwargs.get('first_name', 'Test'),
            last_name=kwargs.get('last_name', 'User'),
        )
        return user
    return _create_user


@pytest.fixture
def create_student(create_user):
    def _create_student(**kwargs):
        user = kwargs.pop('user', None) or create_user()
        student = Student.objects.create(
            user=user,
            student_id=kwargs.get('student_id', 'S1001')
        )
        return student
    return _create_student


@pytest.fixture
def create_class(create_user):
    def _create_class(**kwargs):
        instructor_user = kwargs.pop('instructor_user', None) or create_user(username='instructor', role='INSTRUCTOR')
        class_instance = Class.objects.create(
            class_code=kwargs.get('class_code', 'C101'),
            course=kwargs.get('course'),
            instructor=instructor_user,
            semester=kwargs.get('semester', 'Fall'),
            academic_year=kwargs.get('academic_year', '2025-2026'),
            section=kwargs.get('section', 'A')
        )
        return class_instance
    return _create_class


@pytest.fixture
def create_exam(create_class):
    def _create_exam(**kwargs):
        class_instance = kwargs.pop('class_instance', None) or create_class()
        exam = Exam.objects.create(
            exam_name=kwargs.get('exam_name', 'Midterm'),
            class_instance=class_instance,
            date=kwargs.get('date')
        )
        return exam
    return _create_exam


@pytest.fixture
def create_enrollment(create_student, create_class):
    def _create_enrollment(**kwargs):
        student = kwargs.pop('student', None) or create_student()
        class_instance = kwargs.pop('class_instance', None) or create_class()
        enrollment = Enrollment.objects.create(
            student=student,
            class_instance=class_instance,
            status=kwargs.get('status', 'ENROLLED'),
            grade=kwargs.get('grade'),
            grade_points=kwargs.get('grade_points')
        )
        return enrollment
    return _create_enrollment


@pytest.fixture
def create_grade(create_enrollment, create_user, create_exam):
    def _create_grade(**kwargs):
        enrollment = kwargs.pop('enrollment', None) or create_enrollment()
        exam = kwargs.pop('exam', None) or create_exam(class_instance=enrollment.class_instance)
        graded_by = kwargs.pop('graded_by', None) or create_user(role='INSTRUCTOR')
        grade = Grade.objects.create(
            enrollment=enrollment,
            exam=exam,
            assignment_name=kwargs.get('assignment_name', 'Assignment 1'),
            marks_obtained=kwargs.get('marks_obtained', Decimal('80.00')),
            total_marks=kwargs.get('total_marks', Decimal('100.00')),
            weight_percentage=kwargs.get('weight_percentage', Decimal('50.00')),
            graded_by=graded_by,
            comments=kwargs.get('comments', 'Good work'),
        )
        return grade
    return _create_grade


@pytest.mark.django_db
class TestGradeAPI:
    def test_create_grade_success(self, api_client, create_user, create_enrollment, create_exam):
        instructor = create_user(username='inst1', role='INSTRUCTOR', password='TestPass123!')
        enrollment = create_enrollment(status='ENROLLED')
        exam = create_exam(class_instance=enrollment.class_instance)
        
        # Login as instructor
        api_client.force_authenticate(user=instructor)
        
        url = reverse('grade-list')
        data = {
            'enrollment': str(enrollment.id),
            'exam': str(exam.id),
            'assignment_name': 'Homework 1',
            'marks_obtained': '85.00',
            'total_marks': '100.00',
            'weight_percentage': '20.00',
            'comments': 'Well done'
        }
        
        # Instructor must be the class instructor to grade
        # Make sure instructor is assigned to class
        enrollment.class_instance.instructor = instructor
        enrollment.class_instance.save()
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['assignment_name'] == 'Homework 1'
    
    def test_create_grade_permission_denied_for_wrong_instructor(self, api_client, create_user, create_enrollment, create_exam):
        instructor1 = create_user(username='inst1', role='INSTRUCTOR')
        instructor2 = create_user(username='inst2', role='INSTRUCTOR')
        enrollment = create_enrollment()
        exam = create_exam(class_instance=enrollment.class_instance)
        
        # Instructor2 tries to grade a class taught by instructor1
        enrollment.class_instance.instructor = instructor1
        enrollment.class_instance.save()
        
        api_client.force_authenticate(user=instructor2)
        
        url = reverse('grade-list')
        data = {
            'enrollment': str(enrollment.id),
            'exam': str(exam.id),
            'assignment_name': 'Homework 2',
            'marks_obtained': '90.00',
            'total_marks': '100.00',
            'weight_percentage': '30.00',
            'comments': ''
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['message'] == 'You can only grade your own classes'
    
    def test_update_grade_success(self, api_client, create_user, create_grade):
        instructor = create_user(username='inst1', role='INSTRUCTOR')
        grade = create_grade()
        
        # Assign instructor to class to allow update
        grade.enrollment.class_instance.instructor = instructor
        grade.enrollment.class_instance.save()
        
        api_client.force_authenticate(user=instructor)
        
        url = reverse('grade-detail', kwargs={'pk': grade.id})
        data = {
            'marks_obtained': '95.00',
            'comments': 'Improved'
        }
        
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        grade.refresh_from_db()
        assert float(grade.marks_obtained) == 95.00
        assert grade.comments == 'Improved'
    
    def test_student_can_only_view_own_grades(self, api_client, create_user, create_student, create_enrollment, create_grade):
        student1 = create_student()
        student2 = create_student()
        enrollment1 = create_enrollment(student=student1)
        enrollment2 = create_enrollment(student=student2)
        create_grade(enrollment=enrollment1)
        create_grade(enrollment=enrollment2)
        
        api_client.force_authenticate(user=student1.user)
        
        url = reverse('grade-student-grades', kwargs={'student_id': student1.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Trying to get another student's grades should fail
        url_other = reverse('grade-student-grades', kwargs={'student_id': student2.id})
        response_other = api_client.get(url_other)
        assert response_other.status_code == status.HTTP_403_FORBIDDEN
    
    def test_finalize_grade_success(self, api_client, create_user, create_enrollment):
        instructor = create_user(username='inst1', role='INSTRUCTOR')
        enrollment = create_enrollment(status='ENROLLED')
        enrollment.class_instance.instructor = instructor
        enrollment.class_instance.save()
        
        api_client.force_authenticate(user=instructor)
        
        url = reverse('grade-finalize-grade', kwargs={'enrollment_id': enrollment.id})
        data = {
            'final_grade': 'A',
            'grade_points': '4.00'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        enrollment.refresh_from_db()
        assert enrollment.grade == 'A'
        assert float(enrollment.grade_points) == 4.00
    
    def test_class_statistics(self, api_client, create_user, create_class, create_enrollment, create_grade):
        instructor = create_user(username='inst1', role='INSTRUCTOR')
        class_instance = create_class(instructor_user=instructor)
        enrollment1 = create_enrollment(class_instance=class_instance, status='COMPLETED', grade='A', grade_points=4.00)
        enrollment2 = create_enrollment(class_instance=class_instance, status='COMPLETED', grade='B+', grade_points=3.50)
        
        create_grade(enrollment=enrollment1)
        create_grade(enrollment=enrollment2)
        
        api_client.force_authenticate(user=instructor)
        
        url = reverse('grade-class-statistics', kwargs={'class_id': class_instance.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data['data']
        assert data['statistics']['total_students'] == 2
        assert 'average_grade' in data['statistics']
        assert 'median_grade' in data['statistics']
        assert data['statistics']['grade_distribution']['A'] >= 1 or data['statistics']['grade_distribution']['B+'] >= 1
    
    def test_class_statistics_permission_denied(self, api_client, create_user, create_class):
        instructor1 = create_user(username='inst1', role='INSTRUCTOR')
        instructor2 = create_user(username='inst2', role='INSTRUCTOR')
        class_instance = create_class(instructor_user=instructor1)
        
        api_client.force_authenticate(user=instructor2)
        
        url = reverse('grade-class-statistics', kwargs={'class_id': class_instance.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['message'] == 'You can only view statistics for your own classes'

