"""
Tests for password reset functionality.

This module tests the complete password reset flow, including:
- Requesting password reset
- Token generation and validation
- Password reset confirmation
- Security validations
- Error handling
"""

import pytest
import re
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from unittest.mock import patch


@pytest.mark.django_db
class TestPasswordReset:
    """Tests for the password reset functionality."""

    def test_password_reset_request_success(self, api_client, create_user):
        """Test successful password reset request."""
        # Create user
        user = create_user()

        # Request password reset
        url = reverse("password_reset")
        data = {"email": "test@example.com"}

        # Mock email sending
        with patch("user_management.views.send_mail") as mock_send_mail:
            response = api_client.post(url, data, format="json")

            # Assert successful response
            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.data
            assert (
                "password reset email has been sent" in response.data["message"].lower()
            )

            # Verify email was "sent"
            assert mock_send_mail.called

            # Check email content
            call_args = mock_send_mail.call_args[0]
            assert "Password Reset" in call_args[0]  # Subject
            assert "reset-password" in call_args[1]  # Message
            assert user.email in call_args[3]  # Recipient

    def test_password_reset_request_nonexistent_email(self, api_client):
        """Test password reset request with email that doesn't exist."""
        url = reverse("password_reset")
        data = {"email": "nonexistent@example.com"}

        with patch("user_management.views.send_mail") as mock_send_mail:
            response = api_client.post(url, data, format="json")

            # Should still return success (security - don't reveal if email exists)
            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.data

            # Email should not be sent
            assert not mock_send_mail.called

    def test_password_reset_request_invalid_email_format(self, api_client):
        """Test password reset request with invalid email format."""
        url = reverse("password_reset")
        data = {"email": "not-an-email"}

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_password_reset_confirm_success(
        self, api_client, create_user, create_password_reset_token
    ):
        """Test successful password reset confirmation."""
        # Create user
        user = create_user()

        # Generate reset token
        uid, token = create_password_reset_token(user)

        # Confirm password reset
        url = reverse("password_reset_confirm")
        data = {
            "uid": uid,
            "token": token,
            "password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = api_client.post(url, data, format="json")

        # Assert successful response
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "password has been reset" in response.data["message"].lower()

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password("NewSecurePass123!")

    def test_password_reset_confirm_invalid_token(
        self, api_client, create_user, create_password_reset_token
    ):
        """Test password reset confirmation with invalid token."""
        # Create user
        user = create_user()

        # Generate UID but use invalid token
        uid = create_password_reset_token(user)[0]
        invalid_token = "invalid-token"

        # Attempt confirmation
        url = reverse("password_reset_confirm")
        data = {
            "uid": uid,
            "token": invalid_token,
            "password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data or "error" in response.data

        # Verify password was not changed
        user.refresh_from_db()
        assert user.check_password("Test1234!")

    def test_password_reset_confirm_expired_token(
        self, api_client, create_user, create_password_reset_token
    ):
        """Test password reset confirmation with expired token."""
        # Create user
        user = create_user()

        # Generate reset token
        uid, token = create_password_reset_token(user)

        # Simulate token expiration by changing user's password
        # (which invalidates the token)
        user.set_password("IntermediatePass123!")
        user.save()

        # Attempt confirmation with now-invalid token
        url = reverse("password_reset_confirm")
        data = {
            "uid": uid,
            "token": token,
            "password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify password was not changed to the new one
        user.refresh_from_db()
        assert user.check_password("IntermediatePass123!")

    def test_password_reset_confirm_passwords_dont_match(
        self, api_client, create_user, create_password_reset_token
    ):
        """Test password reset confirmation with mismatched passwords."""
        # Create user
        user = create_user()

        # Generate reset token
        uid, token = create_password_reset_token(user)

        # Attempt confirmation with mismatched passwords
        url = reverse("password_reset_confirm")
        data = {
            "uid": uid,
            "token": token,
            "password": "NewSecurePass123!",
            "confirm_password": "DifferentPass123!",
        }

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data or "confirm_password" in response.data

        # Verify password was not changed
        user.refresh_from_db()
        assert user.check_password("Test1234!")

    def test_password_reset_confirm_weak_password(
        self, api_client, create_user, create_password_reset_token
    ):
        """Test password reset confirmation with weak password."""
        # Create user
        user = create_user()

        # Generate reset token
        uid, token = create_password_reset_token(user)

        # Test several weak passwords
        weak_passwords = [
            "short",  # Too short
            "onlylowercase",  # No uppercase, digits or special chars
            "ONLYUPPERCASE",  # No lowercase, digits or special chars
            "12345678",  # Only digits
            "Password",  # No digits or special chars
        ]

        for password in weak_passwords:
            # Attempt confirmation
            url = reverse("password_reset_confirm")
            data = {
                "uid": uid,
                "token": token,
                "password": password,
                "confirm_password": password,
            }

            response = api_client.post(url, data, format="json")

            # Assert error response
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "password" in response.data

            # Verify password was not changed
            user.refresh_from_db()
            assert user.check_password("Test1234!")

    def test_password_reset_confirm_invalid_uid(self, api_client):
        """Test password reset confirmation with invalid UID."""
        # Use invalid UID
        invalid_uid = "invalid-uid"

        # Attempt confirmation
        url = reverse("password_reset_confirm")
        data = {
            "uid": invalid_uid,
            "token": "some-token",
            "password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data or "error" in response.data

    def test_password_reset_without_required_fields(self, api_client):
        """Test password reset request without required fields."""
        url = reverse("password_reset")
        data = {}  # Missing email

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_password_reset_confirm_without_required_fields(self, api_client):
        """Test password reset confirmation without required fields."""
        url = reverse("password_reset_confirm")
        data = {}  # Missing all required fields

        response = api_client.post(url, data, format="json")

        # Assert error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        assert "token" in response.data
        assert "password" in response.data
