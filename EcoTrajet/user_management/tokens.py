"""
Token generation for email verification.

This module provides token generation functionality for email verification
using Django's PasswordResetTokenGenerator.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import hashlib
from django.utils.encoding import force_bytes


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for account activation/email verification."""

    def _make_hash_value(self, user, timestamp):
        """
        Create a unique hash value for the user.

        This includes the user's primary key, timestamp, and active status
        to ensure the token is unique and becomes invalid when the user's
        status changes.
        """
        # Convert values to strings and concatenate
        login_timestamp = (
            ""
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None).isoformat()
        )

        # Create a unique string based on user data that changes when account is activated
        return f"{user.pk}{timestamp}{user.is_active}{login_timestamp}"


# Create a single instance of the token generator
account_activation_token = AccountActivationTokenGenerator()
