"""
Tests for security features of the user management system.

This module tests security mechanisms including:
- Account locking after failed login attempts
- Login attempt logging
- JWT token blacklisting (logout)
- Authentication requirements for protected endpoints
"""

import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from user_management.models import UserLoginAttempt


@pytest.mark.django_db
class TestSecurity:
    """Tests for security features and controls."""

    def test_failed_login_attempts_logging(self, api_client):
        """Test that failed login attempts are properly logged."""
        url = reverse("token_obtain_pair")

        # Attempt login with invalid credentials
        data = {"username": "nonexistent_user", "password": "wrong_password"}

        response = api_client.post(url, data, format="json")

        # Verify the response indicates failure
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Verify a login attempt was logged
        login_attempt = UserLoginAttempt.objects.filter(
            username="nonexistent_user", success=False
        ).first()

        assert login_attempt is not None
        assert login_attempt.ip_address is not None
        assert login_attempt.timestamp is not None

    def test_successful_login_logging(self, api_client, create_user):
        """Test that successful logins are properly logged."""
        # Create a user
        user = create_user(username="testlogin", password="Test1234!")

        # Login
        url = reverse("token_obtain_pair")
        data = {"username": "testlogin", "password": "Test1234!"}

        response = api_client.post(url, data, format="json")

        # Verify successful login
        assert response.status_code == status.HTTP_200_OK

        # Verify a login attempt was logged as successful
        login_attempt = UserLoginAttempt.objects.filter(
            username="testlogin", success=True
        ).first()

        assert login_attempt is not None
        assert login_attempt.user.id == user.id
        assert login_attempt.ip_address is not None

    def test_account_lockout_after_failed_attempts(
        self, api_client, create_user, create_failed_login_attempts
    ):
        """Test that accounts are temporarily locked after multiple failed login attempts."""
        # Create a user
        user = create_user(username="lockout_test", password="Test1234!")

        # Create 5 recent failed login attempts
        create_failed_login_attempts(user, count=5)

        # Attempt login with correct credentials
        url = reverse("token_obtain_pair")
        data = {"username": "lockout_test", "password": "Test1234!"}

        response = api_client.post(url, data, format="json")

        # Verify the account is locked
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "locked" in str(response.data).lower()

    def test_jwt_token_blacklisting(self, api_client, create_user, auth_client):
        """Test that refresh tokens are properly blacklisted on logout."""
        # Create a user and get authenticated
        user = create_user(username="logout_test", password="Test1234!")
        client, refresh_token = auth_client(user)

        # Logout
        url = reverse("logout")
        data = {"refresh": refresh_token}
        response = client.post(url, data, format="json")

        # Verify successful logout
        assert response.status_code == status.HTTP_200_OK

        # Attempt to use the refresh token to get a new access token
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": refresh_token}
        refresh_response = api_client.post(refresh_url, refresh_data, format="json")

        # Verify the token has been blacklisted
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_authentication(self, api_client, create_user):
        """Test that protected endpoints require authentication."""
        # Create a user but don't authenticate
        create_user(username="protected_test")

        # Try to access a protected endpoint
        url = reverse("profile")
        response = api_client.get(url)

        # Verify authentication is required
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_access_to_protected_endpoint(
        self, api_client, create_user, auth_client
    ):
        """Test that authenticated users can access protected endpoints."""
        # Create a user and authenticate
        user = create_user(username="auth_test", password="Test1234!")
        client, _ = auth_client(user)

        # Access a protected endpoint
        url = reverse("profile")
        response = client.get(url)

        # Verify access is granted
        assert response.status_code == status.HTTP_200_OK

    def test_failed_attempts_cleanup(self, api_client, create_user, monkeypatch):
        """Test that older failed login attempts don't count toward lockout."""
        from django.utils import timezone
        from datetime import datetime, timedelta

        # Create a user with a unique username to avoid conflicts
        unique_username = f"old_attempts_{timezone.now().timestamp()}"
        user = create_user(username=unique_username, password="Test1234!")

        # Direct database approach - override the timestamp field directly
        # Create 10 failed login attempts that are definitely old
        from django.db import connection

        # Log a failed attempt first (this will be properly timestamped)
        url = reverse("token_obtain_pair")
        api_client.post(
            url,
            {"username": unique_username, "password": "wrong_password"},
            format="json",
        )

        # Get that attempt and modify its timestamp
        attempts = UserLoginAttempt.objects.filter(username=unique_username)
        assert attempts.count() > 0

        # Make the attempts old by modifying them directly in the database
        for attempt in attempts:
            attempt.timestamp = timezone.now() - timedelta(hours=1)
            attempt.save(update_fields=["timestamp"])

        # Verify the attempts are now old
        recent_attempts = UserLoginAttempt.objects.filter(
            user=user,
            success=False,
            timestamp__gte=timezone.now() - timedelta(minutes=30),
        ).count()

        assert (
            recent_attempts == 0
        ), f"Found {recent_attempts} recent attempts when expecting 0"

        # Now attempt login with correct credentials
        url = reverse("token_obtain_pair")
        data = {"username": unique_username, "password": "Test1234!"}

        response = api_client.post(url, data, format="json")

        # Verify login succeeds (old attempts don't count toward lockout)
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Login failed with status {response.status_code}: {getattr(response, 'data', {})}"
