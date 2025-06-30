from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime, timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
import re

from user_management.models import UserLoginAttempt


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "roles")

    def get_roles(self, obj):
        return [group.name for group in obj.groups.all()]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data["user"] = UserSerializer(self.user).data

        # Add timestamp in the specified format
        data["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        data["user_login"] = self.user.username

        return data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=["Admin", "Manager", "Employee", "Auditor"],
        write_only=True,
        required=False,
        default="Employee",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "role")
        extra_kwargs = {"email": {"required": True}}

    # In RegisterSerializer class:
    def validate_password(self, value):
        """
        Validate password complexity.
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    # In RegisterSerializer class:
    def validate_email(self, value):
        """
        Check if email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Set user as inactive until email is verified
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_active=False,  # User inactive until verified
        )

        # Assign role
        role = validated_data.pop("role", "Employee")
        group = Group.objects.get(name=role)
        user.groups.add(group)

        # Generate verification token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Send verification email
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
        send_mail(
            "Verify Your Email",
            f"Click the link to verify your email: {verification_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return user


class EmailSerializer(serializers.Serializer):
    """
    Serializer for handling email-based operations like password reset requests.

    This serializer validates that the provided email is correctly formatted.
    It is used in the password reset flow to collect the user's email address
    before sending a reset link.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email is properly formatted.

        Note: We don't validate if the email exists in the database here,
        as this would leak information about registered users.

        Args:
            value: The email to validate

        Returns:
            str: The validated email
        """
        # You could add custom email validation here if needed
        # For example, domain-specific rules or blocking certain domains
        return value

    # Need to add these to EmailSerializer:
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for handling password reset operations.

    This serializer collects and validates:
    - uid: Base64 encoded user ID
    - token: Password reset token
    - password: New password
    - confirm_password: Password confirmation

    It ensures the new password meets the system's security requirements
    and that the confirmation matches.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, min_length=8, write_only=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """
        Validate that the passwords match.

        Args:
            data: The serializer data containing both passwords

        Returns:
            dict: The validated data

        Raises:
            ValidationError: If passwords don't match
        """
        # Check that passwords match
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": ["Passwords do not match."]}
            )
        return attrs

    def validate_password(self, value):
        """
        Validate the password strength.

        Ensures the password meets security requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        - Contains at least one special character

        Args:
            value: The password to validate

        Returns:
            str: The validated password

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        # Check password length
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        # Check for uppercase letter
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        # Check for lowercase letter
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        # Check for digit
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        # Check for special character

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    def validate_uid(self, value):
        """
        Validate that the UID can be decoded.

        Args:
            value: The encoded UID

        Returns:
            str: The validated UID

        Raises:
            ValidationError: If UID is invalid
        """
        try:
            uid = force_str(urlsafe_base64_decode(value))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist, OverflowError) as exc:
            raise serializers.ValidationError("Invalid user identification.") from exc
        return value

    def validate_token(self, value):
        """
        Validate the password reset token.

        Note: This requires validate_uid to be called first,
        which happens automatically in DRF's validation flow.

        Args:
            value: The token to validate

        Returns:
            str: The validated token

        Raises:
            ValidationError: If token is invalid
        """
        if not hasattr(self, "user"):
            # This shouldn't happen as validate_uid should be called first
            raise serializers.ValidationError("Invalid validation order.")

        is_valid = default_token_generator.check_token(self.user, value)
        if not is_valid:
            raise serializers.ValidationError("Invalid or expired token.")
        return value

    # Need to add these to PasswordResetSerializer:
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


# Add these serializers to your existing serializers.py file
def validate_password_strength(password):
    """
    Validate password strength requirements.
    Password must:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one digit
    - Contain at least one special character
    """
    if len(password) < 8:
        raise serializers.ValidationError(
            "Password must be at least 8 characters long."
        )

    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"[0-9]", password):
        raise serializers.ValidationError("Password must contain at least one digit.")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise serializers.ValidationError(
            "Password must contain at least one special character."
        )

    return password


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for handling password change requests.

    Validates old password correctness, new password strength,
    and that confirmation password matches.
    """

    old_password = serializers.CharField(
        required=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        required=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        """Validate that the old password is correct."""
        user = self.context.get("user")
        if user and not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        # Check if passwords match
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords don't match."}
            )

        # Check if new password is same as old password
        if attrs["new_password"] == attrs["old_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from old password."}
            )

        # Validate password strength
        validate_password_strength(attrs["new_password"])

        return attrs

    def create(self, validated_data):
        """Not implemented as this serializer is only used for validation."""
        raise NotImplementedError(
            "PasswordChangeSerializer create method is not implemented."
        )

    def update(self, instance, validated_data):
        """Not implemented as this serializer is only used for validation."""
        raise NotImplementedError(
            "PasswordChangeSerializer update method is not implemented."
        )


class UserLoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginAttempt
        fields = ["username", "ip_address", "timestamp", "success"]
