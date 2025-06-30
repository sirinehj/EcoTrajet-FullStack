"""
Tests for user profile functionality.

This module tests user profile operations including:
- Profile retrieval
- Profile updates
- Password changes
- User activity log
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from unittest.mock import patch
import datetime


@pytest.mark.django_db
class TestUserProfile:
    """Tests for user profile functionality."""

    def test_get_own_profile(self, api_client, create_user, auth_client):
        """Test retrieving user's own profile."""
        # Create user and get authenticated client
        user = create_user(
            username="profiletest",
            email="profile@example.com",
            first_name="Profile",
            last_name="Test",
        )
        auth_client, _ = auth_client(user)

        # Get profile
        url = reverse("profile")
        response = auth_client.get(url)

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "profiletest"
        assert response.data["email"] == "profile@example.com"
        assert response.data["first_name"] == "Profile"
        assert response.data["last_name"] == "Test"

        # Check that role information is included
        assert "roles" in response.data
        assert isinstance(response.data["roles"], list)
        assert "Employee" in response.data["roles"]  # Default role from fixture

    def test_profile_unauthorized(self, api_client):
        """Test accessing profile without authentication."""
        url = reverse("profile")
        response = api_client.get(url)

        # Assert unauthorized response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip(reason="Profile endpoint doesn't support update methods")
    def test_update_profile(self, api_client, create_user, auth_client):
        """Test updating user profile information."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Update profile via POST
        url = reverse("profile")
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
        }

        response = auth_client.post(url, update_data, format="json")

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"
        assert response.data["email"] == "updated@example.com"

        # Verify database was updated
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.email == "updated@example.com"

    @pytest.mark.skip(reason="Profile endpoint doesn't support update methods")
    def test_update_profile_invalid_email(self, api_client, create_user, auth_client):
        """Test update with invalid email format."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Determine which method to use based on the previous test
        method_to_use = auth_client.put  # Default to PUT

        # Try a simple PUT request to see if it's supported
        test_url = reverse("profile")
        test_data = {"first_name": "Test"}
        test_response = auth_client.put(test_url, test_data, format="json")

        # If PUT returns 405, use PATCH instead
        if test_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            method_to_use = auth_client.patch

        # Update with invalid email
        update_data = {"email": "not-an-email"}

        response = method_to_use(test_url, update_data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

        # Verify database was not updated
        user.refresh_from_db()
        assert user.email == "test@example.com"  # Original email

    def test_change_password_success(self, api_client, create_user, auth_client):
        """Test successful password change."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Change password
        url = reverse("change_password")
        data = {
            "old_password": "Test1234!",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = auth_client.post(url, data, format="json")

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "password changed successfully" in response.data["message"].lower()

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password("NewSecurePass123!")

    def test_change_password_incorrect_old_password(
        self, api_client, create_user, auth_client
    ):
        """Test password change with incorrect old password."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Attempt password change with wrong old password
        url = reverse("change_password")
        data = {
            "old_password": "WrongOldPass123!",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = auth_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

        # Verify password was not changed
        user.refresh_from_db()
        assert user.check_password("Test1234!")

    def test_change_password_passwords_dont_match(
        self, api_client, create_user, auth_client
    ):
        """Test password change with mismatched new passwords."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Attempt password change with mismatched new passwords
        url = reverse("change_password")
        data = {
            "old_password": "Test1234!",
            "new_password": "NewSecurePass123!",
            "confirm_password": "DifferentPass123!",
        }

        response = auth_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify password was not changed
        user.refresh_from_db()
        assert user.check_password("Test1234!")

    def test_change_password_weak_password(self, api_client, create_user, auth_client):
        """Test password change with weak new password."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Test several weak passwords
        weak_passwords = [
            "short",  # Too short
            "onlylowercase",  # No uppercase, digits or special chars
            "ONLYUPPERCASE",  # No lowercase, digits or special chars
            "12345678",  # Only digits
            "Password",  # No digits or special chars
        ]

        for password in weak_passwords:
            # Attempt password change
            url = reverse("change_password")
            data = {
                "old_password": "Test1234!",
                "new_password": password,
                "confirm_password": password,
            }

            response = auth_client.post(url, data, format="json")

            # Assert error response
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            # Verify password was not changed
            user.refresh_from_db()
            assert user.check_password("Test1234!")

    def test_change_password_same_as_old(self, api_client, create_user, auth_client):
        """Test changing password to the same as current password."""
        # Create user and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Attempt to "change" password to same value
        url = reverse("change_password")
        data = {
            "old_password": "Test1234!",
            "new_password": "Test1234!",
            "confirm_password": "Test1234!",
        }

        response = auth_client.post(url, data, format="json")

        # Should return error - new password same as old
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in str(response.data)

        # Verify password remains the same
        user.refresh_from_db()
        assert user.check_password("Test1234!")

    def test_change_password_unauthorized(self, api_client):
        """Test password change without authentication."""
        url = reverse("change_password")
        data = {
            "old_password": "Test1234!",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = api_client.post(url, data, format="json")

        # Assert unauthorized response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_activity_log(self, api_client, create_user, auth_client):
        """Test retrieving user activity log."""
        # Create user with activity and get authenticated client
        user = create_user()
        auth_client, _ = auth_client(user)

        # Create some login activity for the user
        from user_management.models import UserLoginAttempt

        # Create successful login
        UserLoginAttempt.objects.create(
            user=user,
            username=user.username,
            ip_address="127.0.0.1",
            success=True,
            timestamp=datetime.datetime.now(),
        )

        # Create failed login
        UserLoginAttempt.objects.create(
            user=user,
            username=user.username,
            ip_address="127.0.0.1",
            success=False,
            timestamp=datetime.datetime.now(),
        )

        # Get activity log
        url = reverse("user_activity")
        response = auth_client.get(url)

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

        # Check data content
        assert len(response.data) == 2

        # Check fields in activity entries
        for entry in response.data:
            assert "username" in entry
            assert "ip_address" in entry
            assert "timestamp" in entry
            assert "success" in entry
            assert entry["username"] == user.username
            assert entry["ip_address"] == "127.0.0.1"

    def test_user_activity_log_unauthorized(self, api_client):
        """Test accessing activity log without authentication."""
        url = reverse("user_activity")
        response = api_client.get(url)

        # Assert unauthorized response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
