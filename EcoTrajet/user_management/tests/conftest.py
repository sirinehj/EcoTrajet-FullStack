"""
Test fixtures for user management app.

This module provides pytest fixtures for testing the authentication system,
including user creation, group setup, and API client configuration.
"""

import pytest
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from datetime import datetime, timedelta


@pytest.fixture
def api_client():
    """
    Return an authenticated API client for testing API endpoints.

    This fixture provides a DRF APIClient instance that can be used to make
    requests to the API endpoints.

    Returns:
        APIClient: An instance of the DRF API client
    """
    return APIClient()


@pytest.fixture
def create_groups():
    """
    Create the user groups required for the application.

    This fixture ensures that all the required groups (Admin, Manager, Employee, Auditor)
    exist in the database for testing role-based permissions.

    Returns:
        list: List of created Group instances
    """
    groups = []
    for group_name in ["Admin", "Manager", "Employee", "Auditor"]:
        group, _ = Group.objects.get_or_create(name=group_name)
        groups.append(group)
    return groups


@pytest.fixture
def create_user(create_groups):
    """
    Factory fixture to create test users with specific roles.

    This fixture returns a function that can be used to create users with
    different attributes and roles for testing.

    Args:
        create_groups: Fixture to ensure groups exist

    Returns:
        function: User creation function that accepts parameters:
            - username: Username for the user (default: 'testuser')
            - password: Password for the user (default: 'Test1234!')
            - email: Email for the user (default: 'test@example.com')
            - role: Role to assign (default: 'Employee')
            - is_active: Whether user is active (default: True)
            - first_name: First name (default: '')
            - last_name: Last name (default: '')
    """

    def _create_user(
        username="testuser",
        password="Test1234!",
        email="test@example.com",
        role="Employee",
        is_active=True,
        first_name="",
        last_name="",
    ):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
        )
        # Assign role
        group = Group.objects.get(name=role)
        user.groups.add(group)
        return user

    return _create_user


@pytest.fixture
def admin_user(create_user):
    """
    Create an admin user for testing admin permissions.

    Returns:
        User: A user with Admin role
    """
    return create_user(
        username="admin",
        email="admin@example.com",
        role="Admin",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def employee_user(create_user):
    """
    Create an employee user for testing standard permissions.

    Returns:
        User: A user with Employee role
    """
    return create_user(
        username="employee",
        email="employee@example.com",
        role="Employee",
        first_name="Regular",
        last_name="Employee",
    )


@pytest.fixture
def manager_user(create_user):
    """
    Create a manager user for testing management permissions.

    Returns:
        User: A user with Manager role
    """
    return create_user(
        username="manager",
        email="manager@example.com",
        role="Manager",
        first_name="Department",
        last_name="Manager",
    )


@pytest.fixture
def auditor_user(create_user):
    """
    Create an auditor user for testing audit permissions.

    Returns:
        User: A user with Auditor role
    """
    return create_user(
        username="auditor",
        email="auditor@example.com",
        role="Auditor",
        first_name="System",
        last_name="Auditor",
    )


@pytest.fixture
def inactive_user(create_user):
    """
    Create an inactive user for testing activation.

    Returns:
        User: An inactive user
    """
    return create_user(
        username="inactive", email="inactive@example.com", is_active=False
    )


@pytest.fixture
def auth_client(api_client):
    """
    Factory fixture to create an authenticated client for a user.

    This fixture returns a function that accepts a user object and returns
    an authenticated API client for that user.

    Args:
        api_client: The API client fixture

    Returns:
        function: Function that accepts a user and returns an authenticated client
    """

    def _get_auth_client(user):
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return api_client, str(refresh)

    return _get_auth_client


@pytest.fixture
def login_user():
    """
    Factory fixture to login a user and get their tokens.

    This fixture returns a function that makes a login request to the API
    and returns the access and refresh tokens.

    Returns:
        function: Function that accepts a client, username, and password
                 and returns access and refresh tokens
    """

    def _login_user(client, username, password):
        url = reverse("token_obtain_pair")
        response = client.post(
            url, {"username": username, "password": password}, format="json"
        )
        return {
            "access": response.data.get("access"),
            "refresh": response.data.get("refresh"),
            "response": response,
        }

    return _login_user


# In conftest.py - fix the create_failed_login_attempts fixture:
@pytest.fixture
def create_failed_login_attempts():
    def _create_failed_attempts(user, count=5, ip_address="127.0.0.1"):
        from user_management.models import UserLoginAttempt
        from django.utils import timezone

        for i in range(count):
            UserLoginAttempt.objects.create(
                user=user,
                username=user.username,
                ip_address=ip_address,
                success=False,
                # Use timezone-aware datetime
                timestamp=timezone.now()
                - timezone.timedelta(minutes=5)
                + timezone.timedelta(seconds=i * 30),
            )

    return _create_failed_attempts


@pytest.fixture
def create_verification_token():
    """
    Factory fixture to create email verification tokens.

    This fixture creates a verification token and UID for a user,
    similar to what would be generated during registration.

    Returns:
        function: Function that accepts a user and returns uid and token
    """

    def _create_verification_token(user):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    return _create_verification_token


@pytest.fixture
def create_password_reset_token():
    """
    Factory fixture to create password reset tokens.

    This fixture creates a password reset token and UID for a user,
    similar to what would be generated during a password reset request.

    Returns:
        function: Function that accepts a user and returns uid and token
    """

    def _create_password_reset_token(user):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    return _create_password_reset_token
