"""
Tests for user management models.

This module contains tests for the UserLoginAttempt model, ensuring that
it correctly tracks and stores login attempts with proper relationships
and ordering.
"""

import pytest
from datetime import datetime, timedelta
import time
from django.contrib.auth.models import User
from user_management.models import UserLoginAttempt
from django.utils import timezone


@pytest.mark.django_db
class TestUserLoginAttempt:
    """Tests for the UserLoginAttempt model."""

    def test_create_login_attempt_with_user(self, create_user):
        """Test creating a login attempt with a user reference."""
        user = create_user(username="testuser", email="test@example.com")

        # Create login attempt linked to user
        login_attempt = UserLoginAttempt.objects.create(
            user=user, username=user.username, ip_address="192.168.1.1", success=True
        )

        # Verify fields
        assert login_attempt.user == user
        assert login_attempt.username == "testuser"
        assert login_attempt.ip_address == "192.168.1.1"
        assert login_attempt.success is True
        assert login_attempt.timestamp is not None

    def test_create_login_attempt_without_user(self):
        """Test creating a login attempt without a user (for non-existent users)."""
        # Create login attempt for non-existent user
        login_attempt = UserLoginAttempt.objects.create(
            user=None,
            username="nonexistentuser",
            ip_address="192.168.1.2",
            success=False,
        )

        # Verify fields
        assert login_attempt.user is None
        assert login_attempt.username == "nonexistentuser"
        assert login_attempt.ip_address == "192.168.1.2"
        assert login_attempt.success is False
        assert login_attempt.timestamp is not None

    def test_create_login_attempt_without_ip(self, create_user):
        """Test creating a login attempt without an IP address."""
        user = create_user(username="iplessuser")

        # Create login attempt without IP
        login_attempt = UserLoginAttempt.objects.create(
            user=user, username=user.username, success=True
        )

        # Verify fields
        assert login_attempt.user == user
        assert login_attempt.ip_address is None
        assert login_attempt.success is True

    def test_default_values(self):
        """Test default values for model fields."""
        # Create with minimal fields
        login_attempt = UserLoginAttempt.objects.create(username="minimaluser")

        # Verify defaults
        assert login_attempt.user is None
        assert login_attempt.ip_address is None
        assert login_attempt.success is False  # Default should be False

    def test_timestamp_auto_set(self):
        """Test that timestamp is automatically set on creation."""
        # Add this import at the top of the file too

        # Create the login attempt
        login_attempt = UserLoginAttempt.objects.create(username="timestampuser")

        # Just verify timestamp exists and is recent
        assert login_attempt.timestamp is not None

        # Timestamp should be within the last minute
        time_diff = timezone.now() - login_attempt.timestamp
        assert time_diff.total_seconds() < 60  # Less than a minute old

    def test_ordering(self, create_user):
        """Test that login attempts are ordered by timestamp (newest first)."""
        user = create_user()

        # Create attempts with different timestamps
        # First attempt (oldest)
        old_attempt = UserLoginAttempt.objects.create(
            user=user, username=user.username, success=False
        )

        # Ensure timestamp difference
        time.sleep(0.01)

        # Second attempt (newest)
        new_attempt = UserLoginAttempt.objects.create(
            user=user, username=user.username, success=True
        )

        # Get all attempts for user (should be ordered by -timestamp)
        attempts = UserLoginAttempt.objects.filter(user=user)

        # First item should be newest
        assert attempts[0].id == new_attempt.id
        assert attempts[1].id == old_attempt.id

    def test_user_deletion_cascade(self, create_user):
        """Test that login attempts are deleted when user is deleted."""
        # Create user and login attempts
        user = create_user()

        UserLoginAttempt.objects.create(user=user, username=user.username, success=True)

        UserLoginAttempt.objects.create(
            user=user, username=user.username, success=False
        )

        # Verify attempts exist
        assert UserLoginAttempt.objects.filter(user=user).count() == 2

        # Delete user
        user.delete()

        # Verify attempts are deleted (CASCADE)
        assert UserLoginAttempt.objects.filter(username=user.username).count() == 0

    def test_recent_failed_attempts_query(
        self, create_user, create_failed_login_attempts
    ):
        """Test query for recent failed login attempts used for account lockout."""

        # Create user and failed login attempts
        user = create_user()
        create_failed_login_attempts(user, count=5)

        # Query used in view for lockout check
        thirty_mins_ago = timezone.now() - timezone.timedelta(minutes=30)
        recent_failed_attempts = UserLoginAttempt.objects.filter(
            user=user, success=False, timestamp__gte=thirty_mins_ago
        ).count()

        # Should find all 5 attempts
        assert recent_failed_attempts == 5

    def test_string_representation(self, create_user):
        """Test the string representation of the model."""
        user = create_user(username="stringuser")
        login_attempt = UserLoginAttempt.objects.create(
            user=user, username=user.username, success=True
        )

        # The model doesn't define __str__, so default representation will be used
        # Just make sure it doesn't error
        str_repr = str(login_attempt)
        assert str_repr is not None
        assert "UserLoginAttempt" in str_repr or "object" in str_repr
