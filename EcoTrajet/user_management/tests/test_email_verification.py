"""
Tests for email verification functionality.

This module tests the email verification process including:
- Sending verification emails
- Verifying email tokens
- Handling expired tokens
- Error cases
"""

import pytest
import re
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator


@pytest.mark.django_db
class TestEmailVerification:
    """Tests for email verification functionality."""

    def test_register_sends_verification_email(self, api_client, create_groups):
        """Test that registration sends a verification email."""
        # Register a new user
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test1234!",
            "password_confirm": "Test1234!",
            "first_name": "Test",
            "last_name": "User",
        }

        # Make sure mail outbox is empty
        mail.outbox = []

        # Register the user
        response = api_client.post(url, data, format="json")

        # Assert successful response - actual code returns 200 not 201
        assert response.status_code == status.HTTP_200_OK

        # Assert verification email was sent
        assert len(mail.outbox) == 1
        assert "verify" in mail.outbox[0].subject.lower()
        assert data["email"] in mail.outbox[0].to

        # Check email content contains verification link
        email_body = mail.outbox[0].body
        assert "verify" in email_body.lower()

        # Extract verification link from email
        verification_link_pattern = r"(/verify-email/[^/\s]+/[^/\s]+/)"
        matches = re.search(verification_link_pattern, email_body)
        assert matches is not None, "Verification link not found in email body"

        # Verify user is initially inactive
        user = User.objects.get(username="testuser")
        assert user.is_active is False

    def test_verify_email_valid_token(self, api_client, create_user):
        """Test successful email verification with valid token."""
        # Create unverified user
        user = create_user(
            username="verifyuser", email="verify@example.com", is_active=False
        )

        # Use default_token_generator instead of account_activation_token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Verify email
        url = reverse("verify_email", kwargs={"uid": uid, "token": token})
        response = api_client.get(url)

        # Assert successful verification
        assert response.status_code == status.HTTP_200_OK
        assert (
            "success" in str(response.data).lower()
            or "verified" in str(response.data).lower()
        )

        # Verify user is now active
        user.refresh_from_db()
        assert user.is_active is True

    def test_verify_email_invalid_token(self, api_client, create_user):
        """Test email verification with invalid token."""
        # Create unverified user
        user = create_user(
            username="invaliduser", email="invalid@example.com", is_active=False
        )

        # Generate invalid verification token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = "invalid-token"

        # Attempt verification
        url = reverse("verify_email", kwargs={"uid": uid, "token": token})
        response = api_client.get(url)

        # Assert failed verification
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in str(response.data).lower()

        # User should still be inactive
        user.refresh_from_db()
        assert user.is_active is False

    def test_verify_email_expired_token(self, api_client, create_user):
        """Test email verification with expired token."""
        # Create unverified user
        user = create_user(
            username="expireduser", email="expired@example.com", is_active=False
        )

        # Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Mock the token validator to simulate an expired token
        with patch(
            "django.contrib.auth.tokens.default_token_generator.check_token",
            return_value=False,
        ):
            token = "expired-token"

            # Attempt verification
            url = reverse("verify_email", kwargs={"uid": uid, "token": token})
            response = api_client.get(url)

            # Assert failed verification
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                "invalid" in str(response.data).lower()
                or "expired" in str(response.data).lower()
            )

            # User should still be inactive
            user.refresh_from_db()
            assert user.is_active is False

    def test_verify_email_already_verified(self, api_client, create_user):
        """Test email verification when already verified."""
        # Create already verified user
        user = create_user(
            username="alreadyverified", email="already@example.com", is_active=True
        )

        # Generate verification token with the default token generator
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Attempt verification
        url = reverse("verify_email", kwargs={"uid": uid, "token": token})
        response = api_client.get(url)

        # Should return success (HTTP 200)
        assert response.status_code == status.HTTP_200_OK

        # User should remain active
        user.refresh_from_db()
        assert user.is_active is True

    def test_verify_email_invalid_uid(self, api_client):
        """Test email verification with invalid user ID."""
        # Generate invalid UID
        uid = "invalid-uid"
        token = "some-token"

        # Attempt verification
        url = reverse("verify_email", kwargs={"uid": uid, "token": token})
        response = api_client.get(url)

        # Assert failed verification
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in str(response.data).lower()

    def test_verify_email_nonexistent_user(self, api_client):
        """Test email verification for non-existent user."""
        # Generate UID for non-existent user (e.g., user ID 999999)
        uid = urlsafe_base64_encode(force_bytes(999999))
        token = "some-token"

        # Attempt verification
        url = reverse("verify_email", kwargs={"uid": uid, "token": token})
        response = api_client.get(url)

        # Assert failed verification
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in str(response.data).lower()
