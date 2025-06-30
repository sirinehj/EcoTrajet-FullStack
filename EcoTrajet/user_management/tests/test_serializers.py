"""
Unit tests for user_management serializers.

This module tests the custom serializers used in the user management app,
including user registration, token claims, password reset, and email validation.
"""

import pytest
from django.contrib.auth.models import User, Group
from django.core import mail
from rest_framework.exceptions import ValidationError

from user_management.serializers import (
    RegisterSerializer,
    EmailSerializer,
    PasswordResetSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_valid_registration(self, create_groups):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Complex123!",
            "first_name": "New",
            "last_name": "User",
            "role": "Employee",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert isinstance(user, User)
        assert user.username == "newuser"
        assert not user.is_active  # Should be inactive until email verified
        assert user.groups.filter(name="Employee").exists()
        # Email should be sent
        assert len(mail.outbox) == 1
        assert "verify your email" in mail.outbox[0].subject.lower()

    def test_missing_required_fields(self, create_groups):
        data = {
            "username": "",
            "email": "invalid",
            "password": "",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors
        assert "email" in serializer.errors
        assert "password" in serializer.errors

    def test_assigns_default_role(self, create_groups):
        data = {
            "username": "defaultrole",
            "email": "role@example.com",
            "password": "Complex123!",
            "first_name": "",
            "last_name": "",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.groups.filter(name="Employee").exists()


@pytest.mark.django_db
class TestEmailSerializer:
    def test_valid_email(self):
        data = {"email": "test@example.com"}
        serializer = EmailSerializer(data=data)
        assert serializer.is_valid()

    def test_invalid_email(self):
        data = {"email": "not-an-email"}
        serializer = EmailSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_empty_email(self):
        data = {"email": ""}
        serializer = EmailSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestPasswordResetSerializer:
    def test_passwords_must_match(self, create_user):
        # Create a real user
        user = create_user(username="resetuser", email="reset@example.com")
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        data = {
            "uid": uid,
            "token": token,
            "password": "Password1!",
            "confirm_password": "Mismatch1!",
        }
        serializer = PasswordResetSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Passwords do not match" in str(excinfo.value)

    def test_password_strength(self, create_user):
        user = create_user(username="resetuser", email="reset@example.com")
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Weak password (no uppercase)
        data = {
            "uid": uid,
            "token": token,
            "password": "weakpassword1!",
            "confirm_password": "weakpassword1!",
        }
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert "Password must contain at least one uppercase letter." in str(
            serializer.errors
        )

        # Weak password (too short)
        data["password"] = data["confirm_password"] = "Sh0rt!"
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert "at least 8 characters" in str(serializer.errors).lower()

        # Strong password
        data["password"] = data["confirm_password"] = "StrongPass1!"
        serializer = PasswordResetSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_uid(self):
        data = {
            "uid": "invaliduid",
            "token": "sometoken",
            "password": "Password1!",
            "confirm_password": "Password1!",
        }
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert "Invalid user identification" in str(serializer.errors)

    def test_invalid_token(self, create_user):
        user = create_user(username="tokentest", email="tokentest@example.com")
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        data = {
            "uid": uid,
            "token": "invalidtoken",
            "password": "Password1!",
            "confirm_password": "Password1!",
        }
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert "Invalid or expired token" in str(serializer.errors)


@pytest.mark.django_db
def test_user_serializer_fields(create_user):
    user = create_user(
        username="serialuser", email="serial@example.com", role="Manager"
    )
    serializer = UserSerializer(user)
    data = serializer.data
    assert data["username"] == "serialuser"
    assert data["email"] == "serial@example.com"
    assert data["roles"] == ["Manager"]


@pytest.mark.django_db
def test_custom_token_obtain_pair_serializer(create_user):
    user = create_user(username="jwtuser", email="jwtuser@example.com")

    class DummyRequest:
        pass

    serializer = CustomTokenObtainPairSerializer()
    serializer.user = user
    attrs = {"username": "jwtuser", "password": "Test1234!"}
    data = serializer.validate(attrs)
    assert "user" in data
    assert data["user"]["username"] == "jwtuser"
    assert "timestamp" in data
    assert data["user_login"] == "jwtuser"
