"""
Test suite for authentication and user management.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from faker import Faker

fake = Faker()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def create_user():
    """Factory to create users with unique emails."""
    def _create_user(**kwargs):
        defaults = {
            'username': kwargs.get('username', f'user_{fake.unique.user_name()}'),
            'email': kwargs.get('email', fake.unique.email()),
            'first_name': kwargs.get('first_name', 'Test'),
            'last_name': kwargs.get('last_name', 'User'),
            'role': kwargs.get('role', 'STUDENT'),
        }
        password = kwargs.get('password', 'TestPass123!')
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return _create_user


@pytest.mark.django_db
class TestAuthentication:
    """Tests for authentication endpoints."""

    def test_user_login_success(self, api_client, create_user):
        user = create_user(username='loginuser', password='TestPass123!')
        url = reverse('auth-login')
        data = {'username': user.username, 'password': 'TestPass123!'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']

    def test_user_login_invalid_credentials(self, api_client, create_user):
        user = create_user(username='loginuser2', password='TestPass123!')
        url = reverse('auth-login')
        data = {'username': user.username, 'password': 'WrongPass!'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_logout(self, api_client, create_user):
        user = create_user()
        login_url = reverse('auth-login')
        login_data = {'username': user.username, 'password': 'TestPass123!'}
        login_response = api_client.post(login_url, login_data, format='json')

        access_token = login_response.data['data']['access_token']
        refresh_token = login_response.data['data']['refresh_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_url = reverse('auth-logout')
        response = api_client.post(logout_url, {'refresh_token': refresh_token}, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_password_reset_request(self, api_client, create_user):
        user = create_user()
        url = reverse('auth-password-reset')
        data = {'email': user.email}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.password_reset_token is not None


@pytest.mark.django_db
class TestUserManagement:
    """Tests for user management endpoints."""

    def test_create_user_as_admin(self, api_client, create_user):
        admin = create_user(username='admin', role='ADMIN', password='AdminPass123!')
        login_url = reverse('auth-login')
        login_data = {'username': admin.username, 'password': 'AdminPass123!'}
        access_token = api_client.post(login_url, login_data, format='json').data['data']['access_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('users-list')
        data = {
            'username': 'newuser',
            'email': fake.unique.email(),
            'password': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'STUDENT'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()

    def test_list_users_as_admin(self, api_client, create_user):
        admin = create_user(username='admin', role='ADMIN', password='AdminPass123!')
        create_user(username='user1')
        create_user(username='user2')

        login_url = reverse('auth-login')
        access_token = api_client.post(
            login_url, {'username': 'admin', 'password': 'AdminPass123!'}, format='json'
        ).data['data']['access_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('users-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 3

    def test_update_user_as_admin(self, api_client, create_user):
        admin = create_user(username='admin', role='ADMIN', password='AdminPass123!')
        user = create_user(username='updatable_user')

        login_url = reverse('auth-login')
        access_token = api_client.post(
            login_url, {'username': 'admin', 'password': 'AdminPass123!'}, format='json'
        ).data['data']['access_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('users-detail', kwargs={'pk': user.id})
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'

    def test_assign_role(self, api_client, create_user):
        admin = create_user(username='admin', role='ADMIN', password='AdminPass123!')
        user = create_user(username='role_user')

        login_url = reverse('auth-login')
        access_token = api_client.post(
            login_url, {'username': 'admin', 'password': 'AdminPass123!'}, format='json'
        ).data['data']['access_token']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('users-assign-role', kwargs={'pk': user.id})
        data = {'role': 'INSTRUCTOR'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.role == 'INSTRUCTOR'
