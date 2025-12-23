"""
Test suite for notifications, messaging, and student requests.
"""
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date

from accounts.models import User
from students.models import Student
from notifications.models import Notification, Message, StudentRequest

# ------------------------------------------------------------------
# Fixtures (Shared)
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
def student_user(create_user):
    return create_user(username='student1', role='STUDENT')

@pytest.fixture
def other_student_user(create_user):
    return create_user(username='student2', role='STUDENT')

@pytest.fixture
def admin_user(create_user):
    return create_user(username='admin', role='ADMIN')

@pytest.fixture
def student_profile(student_user):
    return Student.objects.create(
        user=student_user,
        student_id='STU001',
        date_of_birth='2000-01-01',
        gender='MALE',
        address="123 St",
        city="City",
        enrollment_date='2025-01-01'
    )

@pytest.fixture
def auth_student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client

@pytest.fixture
def auth_admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

# ------------------------------------------------------------------
# Tests: Notifications
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestNotificationViewSet:

    def test_list_notifications(self, auth_student_client, student_user):
        Notification.objects.create(recipient=student_user, title="Msg 1", notification_type="SYSTEM")
        Notification.objects.create(recipient=student_user, title="Msg 2", notification_type="GRADE")
        
        # URL FIX: 'notifications-list'
        url = reverse('notifications-list')
        response = auth_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['unread_count'] == 2
        assert len(response.data['data']['results']) == 2

    def test_mark_read_action(self, auth_student_client, student_user):
        notif = Notification.objects.create(
            recipient=student_user, title="Test", is_read=False, notification_type="SYSTEM"
        )
        
        # URL FIX: 'notifications-mark-read'
        url = reverse('notifications-mark-read', kwargs={'pk': notif.id})
        response = auth_student_client.put(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        notif.refresh_from_db()
        assert notif.is_read is True

    def test_mark_all_read_action(self, auth_student_client, student_user):
        Notification.objects.create(recipient=student_user, title="1", is_read=False, notification_type="SYSTEM")
        Notification.objects.create(recipient=student_user, title="2", is_read=False, notification_type="SYSTEM")
        
        # URL FIX: 'notifications-mark-all-read'
        url = reverse('notifications-mark-all-read')
        response = auth_student_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['updated_count'] == 2
        assert Notification.objects.filter(recipient=student_user, is_read=False).count() == 0

    def test_cannot_delete_others_notification(self, auth_student_client, admin_user):
        notif = Notification.objects.create(recipient=admin_user, title="Admin Msg", notification_type="SYSTEM")
        
        # URL FIX: 'notifications-detail'
        url = reverse('notifications-detail', kwargs={'pk': notif.id})
        response = auth_student_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ------------------------------------------------------------------
# Tests: Messaging
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestMessageViewSet:

    def test_send_message(self, auth_student_client, student_user, other_student_user):
        # URL FIX: 'messages-list'
        url = reverse('messages-list')
        data = {
            "recipient_id": str(other_student_user.id),
            "subject": "Hello",
            "body": "How are you?"
        }
        
        response = auth_student_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Message.objects.count() == 1
        assert Message.objects.first().sender == student_user

    def test_list_inbox(self, auth_student_client, student_user, other_student_user):
        Message.objects.create(sender=other_student_user, recipient=student_user, subject="In", body="b")
        Message.objects.create(sender=student_user, recipient=other_student_user, subject="Out", body="b")
        
        # URL FIX: 'messages-list'
        url = reverse('messages-list') + "?folder=inbox"
        response = auth_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['data']['results']
        assert len(results) == 1
        assert results[0]['subject'] == "In"

    def test_retrieve_marks_as_read(self, auth_student_client, student_user, other_student_user):
        msg = Message.objects.create(
            sender=other_student_user, 
            recipient=student_user, 
            subject="Read Me", 
            body="test", 
            is_read=False
        )
        
        # URL FIX: 'messages-detail'
        url = reverse('messages-detail', kwargs={'pk': msg.id})
        response = auth_student_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        msg.refresh_from_db()
        assert msg.is_read is True

    def test_delete_message_permission(self, auth_student_client, admin_user, other_student_user):
        msg = Message.objects.create(sender=admin_user, recipient=other_student_user, subject="Private", body="x")
        
        # URL FIX: 'messages-detail'
        url = reverse('messages-detail', kwargs={'pk': msg.id})
        response = auth_student_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ------------------------------------------------------------------
# Tests: Student Requests
# ------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentRequestViewSet:

    def test_create_request_as_student(self, auth_student_client, student_profile):
        # URL FIX: 'student-requests-list' (matches basename='student-requests')
        url = reverse('student-requests-list')
        data = {
            "student": str(student_profile.id),
            "request_type": "TRANSCRIPT",
            "subject": "Need transcript",
            "description": "For grad school"
        }
        
        response = auth_student_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert StudentRequest.objects.count() == 1
        assert StudentRequest.objects.first().status == 'PENDING'

    def test_student_cannot_update_request_status(self, auth_student_client, student_profile):
        req = StudentRequest.objects.create(
            student=student_profile,
            request_type="TRANSCRIPT",
            subject="Test",
            description="Desc",
            status="PENDING"
        )
        
        # URL FIX: 'student-requests-detail'
        url = reverse('student-requests-detail', kwargs={'pk': req.id})
        data = {"status": "APPROVED"}
        
        response = auth_student_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch('core.notifications.RequestNotificationTrigger.on_request_status_changed')
    def test_admin_update_request_status(self, mock_trigger, auth_admin_client, student_profile):
        req = StudentRequest.objects.create(
            student=student_profile,
            request_type="TRANSCRIPT",
            subject="Test",
            description="Desc",
            status="PENDING"
        )
        
        # URL FIX: 'student-requests-detail'
        url = reverse('student-requests-detail', kwargs={'pk': req.id})
        data = {"status": "APPROVED", "response": "Approved by Admin"}
        
        response = auth_admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        req.refresh_from_db()
        assert req.status == 'APPROVED'
        
        # Verify notification was triggered
        mock_trigger.assert_called_once()