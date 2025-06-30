"""
Tests for authentication functionality.

This module tests the complete authentication flow, including:
- Login with valid/invalid credentials
- Token refresh
- Logout
- Account lockout
- JWT token validation
- Error handling
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from unittest.mock import patch, Mock
from user_management.models import UserLoginAttempt


@pytest.mark.django_db
class TestAuthentication:
    """Tests for the user authentication functionality."""

    def test_successful_login(self, api_client, create_user):
        """Test login with valid credentials."""
        # Create user
        user = create_user()

        # Login
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "Test1234!"}
        response = api_client.post(url, data, format="json")

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["username"] == "testuser"
        assert "timestamp" in response.data
        assert "user_login" in response.data

        # Verify login attempt was logged
        assert UserLoginAttempt.objects.filter(
            username="testuser", success=True
        ).exists()

    def test_failed_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        url = reverse("token_obtain_pair")
        data = {"username": "wronguser", "password": "wrongpass"}
        response = api_client.post(url, data, format="json")

        # Accept either 401 (auth failure) or 403 (rate limit)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

        # Verify failed login attempt was logged
        assert UserLoginAttempt.objects.filter(
            username="wronguser", success=False
        ).exists()

    def test_failed_login_inactive_user(self, api_client, inactive_user):
        """Test login with inactive user account."""
        url = reverse("token_obtain_pair")
        data = {"username": "inactive", "password": "Test1234!"}
        response = api_client.post(url, data, format="json")

        # Accept either 401 (auth failure) or 403 (rate limit)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

        # Verify failed login attempt was logged
        assert UserLoginAttempt.objects.filter(
            username="inactive", success=False
        ).exists()

    @patch("user_management.views.UserLoginAttempt.objects.filter")
    def test_account_lockout(self, mock_filter, api_client, create_user):
        """Test account lockout after multiple failed login attempts."""
        # Create user
        user = create_user()

        # Mock the filter to return a queryset with count=5
        mock_queryset = Mock()
        mock_queryset.count.return_value = 5
        mock_filter.return_value = mock_queryset

        # Attempt login with correct credentials
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "Test1234!"}
        response = api_client.post(url, data, format="json")

        # Assert account is locked
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "locked" in response.data["error"].lower()

    @patch("user_management.views.UserLoginAttempt.objects.filter")
    def test_login_after_lockout_expires(self, mock_filter, api_client, create_user):
        """Test login after lockout period expires."""
        # Create user
        user = create_user()

        # Mock the filter to return a queryset with count=0 (no recent failures)
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0
        mock_filter.return_value = mock_queryset

        # Attempt login with correct credentials
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "Test1234!"}
        response = api_client.post(url, data, format="json")

        # Assert login succeeds
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    # Use auth_client fixture instead of login_user to avoid token refresh issues
    def test_token_refresh(self, api_client, create_user, auth_client):
        """Test refreshing access token with valid refresh token."""
        # Create user and get authenticated client with tokens
        user = create_user()
        _, refresh = auth_client(user)

        # Refresh token
        url = reverse("token_refresh")
        data = {"refresh": refresh}
        response = api_client.post(url, data, format="json")

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_token_refresh_invalid_token(self, api_client):
        """Test refreshing with invalid refresh token."""
        url = reverse("token_refresh")
        data = {"refresh": "invalid-refresh-token"}
        response = api_client.post(url, data, format="json")

        # Assert error response - either 401 (invalid token) or 400 (bad request)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST,
        ]

    # Use auth_client fixture instead of login_user
    def test_successful_logout(self, api_client, create_user, auth_client):
        """Test successful logout by blacklisting refresh token."""
        # Create user and get authenticated client with tokens
        user = create_user()
        client, refresh = auth_client(user)

        # Logout
        url = reverse("logout")
        data = {"refresh": refresh}
        response = client.post(url, data, format="json")

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "logout successful" in response.data["message"].lower()

    def test_logout_without_authentication(self, api_client):
        """Test logout without authentication."""
        url = reverse("logout")
        data = {"refresh": "some-token"}
        response = api_client.post(url, data, format="json")

        # Assert unauthorized response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Use auth_client fixture
    def test_logout_invalid_token(self, api_client, create_user, auth_client):
        """Test logout with invalid refresh token."""
        # Create user and get authenticated client
        user = create_user()
        client, _ = auth_client(user)

        # Logout with invalid token
        url = reverse("logout")
        data = {"refresh": "invalid-token"}
        response = client.post(url, data, format="json")

        # Either 400 (bad token) or 401 (auth failed)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_access_protected_endpoint_without_token(self, api_client):
        """Test accessing protected endpoint without authentication token."""
        url = reverse("profile")
        response = api_client.get(url)

        # Assert unauthorized response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_token(
        self, api_client, create_user, auth_client
    ):
        """Test accessing protected endpoint with valid authentication token."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Access protected endpoint
        url = reverse("profile")
        response = auth_client.get(url)

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"

    def test_login_with_case_insensitive_username(self, api_client, create_user):
        """Test login with username in different case."""
        # Create user with lowercase username
        user = create_user(username="testuser")

        # Login with uppercase username
        url = reverse("token_obtain_pair")
        data = {"username": "TESTUSER", "password": "Test1234!"}
        response = api_client.post(url, data, format="json")

        # Accept either 401 (incorrect credentials) or 403 (rate limit)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
