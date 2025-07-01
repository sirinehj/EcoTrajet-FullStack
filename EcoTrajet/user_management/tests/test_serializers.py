"""
Tests for user management serializers.
"""
import re
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from user_management.models import User, UserLoginAttempt
from user_management.serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    EmailSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer,
    UserLoginAttemptSerializer,
    validate_password_strength,
)


@pytest.fixture
def user_data():
    """Fixture for user data."""
    return {
        "email": "test@example.com",
        "password": "Password1!",
        "nom": "Test",
        "prenom": "User",
        "role": "passager",
        "telephone": "1234567890",
    }


@pytest.fixture
@pytest.mark.django_db
def user(user_data):
    """Fixture for creating a user."""
    return User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        nom=user_data["nom"],
        prenom=user_data["prenom"],
        role=user_data["role"],
        telephone=user_data["telephone"]
    )


@pytest.fixture
@pytest.mark.django_db
def admin_user():
    """Fixture for creating an admin user."""
    return User.objects.create_user(
        email="admin@example.com",
        password="AdminPass1!",
        nom="Admin",
        prenom="User",
        role="admin",
        is_staff=True,
        is_active=True,
    )


@pytest.mark.django_db
class TestUserSerializer:
    """Tests for UserSerializer."""

    def test_user_serialization(self, user):
        """Test that UserSerializer correctly serializes a User instance."""
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert "idUser" in data
        assert data["email"] == user.email
        assert data["nom"] == user.nom
        assert data["prenom"] == user.prenom
        assert data["role"] == user.role
        assert data["telephone"] == user.telephone
        assert data["is_active"] == user.is_active
        assert "password" not in data  # Ensure password is not serialized
    
    def test_serializer_fields(self):
        """Test that UserSerializer has the correct fields."""
        serializer = UserSerializer()
        assert set(serializer.Meta.fields) == {
            "idUser", "email", "nom", "prenom", "role", "telephone", "is_active"
        }


@pytest.mark.django_db
class TestCustomTokenObtainPairSerializer:
    """Tests for CustomTokenObtainPairSerializer."""

    @patch("user_management.serializers.TokenObtainPairSerializer.validate")
    def test_validate_adds_custom_claims(self, mock_validate, user):
        """Test that validate adds custom claims to the token data."""
        # Setup mock return value
        mock_validate.return_value = {"access": "mock-access-token", "refresh": "mock-refresh-token"}
        
        # Create serializer instance
        serializer = CustomTokenObtainPairSerializer()
        serializer.user = user
        
        # Call validate
        data = serializer.validate({"email": user.email, "password": "Password1!"})
        
        # Assertions
        assert "user" in data
        assert data["user"]["idUser"] == user.idUser
        assert data["user"]["email"] == user.email
        assert data["user"]["nom"] == user.nom
        assert data["user"]["prenom"] == user.prenom
        assert data["user"]["role"] == user.role
        
        # Check timestamp format
        assert "timestamp" in data
        # Verify timestamp is in the expected format YYYY-MM-DD HH:MM:SS
        datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
        
        assert data["user_login"] == user.email


@pytest.mark.django_db
class TestRegisterSerializer:
    """Tests for RegisterSerializer."""

    def test_valid_registration(self, user_data):
        """Test registration with valid data."""
        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid(), f"Validation errors: {serializer.errors}"
        
        with patch("user_management.serializers.send_mail") as mock_send_mail:
            user = serializer.save()
            assert user.email == user_data["email"]
            assert user.nom == user_data["nom"]
            assert user.prenom == user_data["prenom"]
            assert user.role == user_data["role"]
            assert user.telephone == user_data["telephone"]
            assert not user.is_active  # User should be inactive until verified
            assert user.check_password(user_data["password"])
    
    def test_default_role(self):
        """Test that role defaults to 'passager' if not provided."""
        data = {
            "email": "new@example.com",
            "password": "Password1!",
            "nom": "New",
            "prenom": "User",
            "telephone": "1234567890",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), f"Validation errors: {serializer.errors}"
        
        with patch("user_management.serializers.send_mail"):
            user = serializer.save()
            assert user.role == 'passager'
    
    def test_password_validation(self):
        """Test password validation rules."""
        test_cases = [
            ("short", "Password must be at least 8 characters long"),
            ("lowercase1!", "Password must contain at least one uppercase letter"),
            ("UPPERCASE1!", "Password must contain at least one lowercase letter"),
            ("Passwordabc!", "Password must contain at least one number"),
            ("Password123", "Password must contain at least one special character"),
        ]
        
        for password, expected_error in test_cases:
            serializer = RegisterSerializer()
            with pytest.raises(ValidationError) as excinfo:
                serializer.validate_password(password)
            assert expected_error in str(excinfo.value)
    
    def test_email_already_exists(self, user):
        """Test that registration fails if email already exists."""
        serializer = RegisterSerializer()
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_email(user.email)
        assert "A user with this email already exists" in str(excinfo.value)
    
    def test_email_required(self):
        """Test that email is required."""
        data = {
            "password": "Password1!",
            "nom": "Test",
            "prenom": "User",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
    
    @patch("user_management.serializers.send_mail")
    def test_verification_email_sent(self, mock_send_mail, user_data):
        """Test that verification email is sent on registration."""
        # Configure test settings
        with patch("user_management.serializers.settings") as mock_settings:
            mock_settings.FRONTEND_URL = "https://example.com"
            mock_settings.DEFAULT_FROM_EMAIL = "noreply@example.com"
            
            serializer = RegisterSerializer(data=user_data)
            assert serializer.is_valid()
            user = serializer.save()
            
            # Check that send_mail was called
            assert mock_send_mail.called
            call_args = mock_send_mail.call_args[0]
            assert call_args[0] == "Verify Your Email"
            # Check that the verification link uses the correct URL pattern from your urls.py
            verification_link = call_args[1]
            assert "verify-email" in verification_link
            assert mock_settings.FRONTEND_URL in verification_link
            assert call_args[2] == mock_settings.DEFAULT_FROM_EMAIL
            assert call_args[3] == [user.email]


class TestEmailSerializer:
    """Tests for EmailSerializer."""

    def test_email_validation(self):
        """Test email validation."""
        # Valid email
        serializer = EmailSerializer(data={"email": "valid@example.com"})
        assert serializer.is_valid()
        
        # Invalid email
        serializer = EmailSerializer(data={"email": "invalid-email"})
        assert not serializer.is_valid()
        assert "email" in serializer.errors
    
    def test_email_required(self):
        """Test that email is required."""
        serializer = EmailSerializer(data={})
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestPasswordResetSerializer:
    """Tests for PasswordResetSerializer."""

    @pytest.fixture
    def reset_data(self, user):
        """Fixture for password reset data."""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return {
            "uid": uid,
            "token": token,
            "password": "NewPassword1!",
            "confirm_password": "NewPassword1!",
        }
    
    def test_valid_reset_data(self, reset_data, user):
        """Test password reset with valid data."""
        serializer = PasswordResetSerializer(data=reset_data)
        # Manually set user for test
        serializer.user = user
        
        # First validate uid separately
        serializer.validate_uid(reset_data["uid"])
        # Then validate token
        serializer.validate_token(reset_data["token"])
        # Then validate the whole data
        assert serializer.validate(reset_data) == reset_data
    
    def test_passwords_do_not_match(self, reset_data, user):
        """Test validation fails if passwords don't match."""
        reset_data["confirm_password"] = "DifferentPassword1!"
        serializer = PasswordResetSerializer(data=reset_data)
        # Manually set user for test
        serializer.user = user
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate(reset_data)
        assert "Passwords do not match" in str(excinfo.value)
    
    def test_invalid_uid(self, reset_data):
        """Test validation fails with invalid uid."""
        reset_data["uid"] = "invalid-uid"
        serializer = PasswordResetSerializer(data=reset_data)
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_uid(reset_data["uid"])
        assert "Invalid user identification" in str(excinfo.value)
    
    def test_invalid_token(self, reset_data, user):
        """Test validation fails with invalid token."""
        reset_data["token"] = "invalid-token"
        serializer = PasswordResetSerializer(data=reset_data)
        # Manually set user for test
        serializer.user = user
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_token(reset_data["token"])
        assert "Invalid or expired token" in str(excinfo.value)
    
    def test_password_strength_validation(self, reset_data, user):
        """Test password strength validation."""
        # Test with weak password
        reset_data["password"] = "weak"
        reset_data["confirm_password"] = "weak"
        serializer = PasswordResetSerializer(data=reset_data)
        # Manually set user for test
        serializer.user = user
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_password(reset_data["password"])
        assert "at least 8 characters" in str(excinfo.value)
    
    def test_required_fields(self):
        """Test that all fields are required."""
        serializer = PasswordResetSerializer(data={})
        assert not serializer.is_valid()
        assert "uid" in serializer.errors
        assert "token" in serializer.errors
        assert "password" in serializer.errors
        assert "confirm_password" in serializer.errors


@pytest.mark.django_db
class TestPasswordChangeSerializer:
    """Tests for PasswordChangeSerializer."""

    @pytest.fixture
    def change_data(self):
        """Fixture for password change data."""
        return {
            "old_password": "Password1!",
            "new_password": "NewPassword2@",
            "confirm_password": "NewPassword2@",
        }
    
    def test_valid_password_change(self, change_data, user):
        """Test password change with valid data."""
        # Ensure the old password matches what's in the fixture
        user.set_password(change_data["old_password"])
        user.save()
        
        serializer = PasswordChangeSerializer(
            data=change_data, context={"user": user}
        )
        assert serializer.is_valid(), f"Validation errors: {serializer.errors}"
    
    def test_incorrect_old_password(self, change_data, user):
        """Test validation fails if old password is incorrect."""
        # Set a different password than what's in the change_data
        user.set_password("DifferentPassword1!")
        user.save()
        
        serializer = PasswordChangeSerializer(
            data=change_data, context={"user": user}
        )
        assert not serializer.is_valid()
        assert "old_password" in serializer.errors
        assert "Old password is incorrect" in str(serializer.errors["old_password"][0])
    
    def test_passwords_dont_match(self, change_data, user):
        """Test validation fails if new passwords don't match."""
        # Ensure the old password matches
        user.set_password(change_data["old_password"])
        user.save()
        
        change_data["confirm_password"] = "DifferentPassword3#"
        serializer = PasswordChangeSerializer(
            data=change_data, context={"user": user}
        )
        assert not serializer.is_valid()
        assert "confirm_password" in serializer.errors
    
    def test_new_password_same_as_old(self, change_data, user):
        """Test validation fails if new password is same as old."""
        # Ensure the old password matches
        user.set_password(change_data["old_password"])
        user.save()
        
        change_data["new_password"] = change_data["old_password"]
        change_data["confirm_password"] = change_data["old_password"]
        
        serializer = PasswordChangeSerializer(
            data=change_data, context={"user": user}
        )
        assert not serializer.is_valid()
        assert "new_password" in serializer.errors
    
    def test_required_fields(self):
        """Test that all fields are required."""
        serializer = PasswordChangeSerializer(data={})
        assert not serializer.is_valid()
        assert "old_password" in serializer.errors
        assert "new_password" in serializer.errors
        assert "confirm_password" in serializer.errors


@pytest.mark.django_db
class TestUserLoginAttemptSerializer:
    """Tests for UserLoginAttemptSerializer."""

    def test_login_attempt_serialization(self):
        """Test that UserLoginAttemptSerializer correctly serializes a login attempt."""
        login_attempt = UserLoginAttempt.objects.create(
            username="test@example.com",
            ip_address="127.0.0.1",
            success=True
        )
        
        serializer = UserLoginAttemptSerializer(login_attempt)
        data = serializer.data
        
        assert data["username"] == login_attempt.username
        assert data["ip_address"] == login_attempt.ip_address
        assert data["success"] == login_attempt.success
        assert "timestamp" in data
    
    def test_serializer_fields(self):
        """Test that UserLoginAttemptSerializer has the correct fields."""
        serializer = UserLoginAttemptSerializer()
        assert set(serializer.Meta.fields) == {"username", "ip_address", "timestamp", "success"}


class TestPasswordStrengthValidator:
    """Tests for password_strength_validator function."""
    
    def test_valid_password(self):
        """Test validation of a strong password."""
        assert validate_password_strength("StrongP@ss1") == "StrongP@ss1"
    
    def test_short_password(self):
        """Test validation fails for short passwords."""
        with pytest.raises(ValidationError) as excinfo:
            validate_password_strength("Short1!")
        assert "at least 8 characters" in str(excinfo.value)
    
    def test_no_uppercase(self):
        """Test validation fails for passwords without uppercase letters."""
        with pytest.raises(ValidationError) as excinfo:
            validate_password_strength("password1!")
        assert "uppercase letter" in str(excinfo.value)
    
    def test_no_lowercase(self):
        """Test validation fails for passwords without lowercase letters."""
        with pytest.raises(ValidationError) as excinfo:
            validate_password_strength("PASSWORD1!")
        assert "lowercase letter" in str(excinfo.value)
    
    def test_no_digit(self):
        """Test validation fails for passwords without digits."""
        with pytest.raises(ValidationError) as excinfo:
            validate_password_strength("Password!")
        assert "one digit" in str(excinfo.value)
    
    def test_no_special_char(self):
        """Test validation fails for passwords without special characters."""
        with pytest.raises(ValidationError) as excinfo:
            validate_password_strength("Password1")
        assert "special character" in str(excinfo.value)