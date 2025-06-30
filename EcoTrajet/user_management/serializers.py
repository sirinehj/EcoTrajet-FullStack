"""
Serializers for user management authentication system.
"""
import re
from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user_management.models import User, UserLoginAttempt


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        """Meta configuration for UserSerializer."""
        model = User
        fields = ("idUser", "email", "nom", "prenom", "role", "telephone", "is_active")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""
    
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data["user"] = UserSerializer(self.user).data

        # Add timestamp in the specified format
        data["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        data["user_login"] = self.user.email

        return data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=[
            ('passager', 'Passager'),
            ('conducteur', 'Conducteur'),
            ('admin', 'Admin'),
        ],
        write_only=True,
        required=False,
        default='passager',
    )

    class Meta:
        """Meta configuration for RegisterSerializer."""
        model = User
        fields = ("email", "password", "nom", "prenom", "role", "telephone")
        extra_kwargs = {"email": {"required": True}}

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

    def validate_email(self, value):
        """
        Check if email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Extract role before creating user
        role = validated_data.pop('role', 'passager')
        
        # Create user with your custom User model
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nom=validated_data.get("nom", ""),
            prenom=validated_data.get("prenom", ""),
            telephone=validated_data.get("telephone", ""),
            role=role,
            is_active=False,  # User inactive until verified
        )

        # Generate verification token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Send verification email (only if settings are configured)
        if hasattr(settings, 'FRONTEND_URL') and hasattr(settings, 'DEFAULT_FROM_EMAIL'):
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
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email is properly formatted.
        """
        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for handling password reset operations.
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
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": ["Passwords do not match."]}
            )
        return attrs

    def validate_password(self, value):
        """
        Validate the password strength.
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

    def validate_uid(self, value):
        """
        Validate that the UID can be decoded.
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
        """
        if not hasattr(self, "user"):
            raise serializers.ValidationError("Invalid validation order.")

        is_valid = default_token_generator.check_token(self.user, value)
        if not is_valid:
            raise serializers.ValidationError("Invalid or expired token.")
        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


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
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords don't match."}
            )

        if attrs["new_password"] == attrs["old_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from old password."}
            )

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
    """Serializer for UserLoginAttempt model."""
    
    class Meta:
        """Meta configuration for UserLoginAttemptSerializer."""
        model = UserLoginAttempt
        fields = ["username", "ip_address", "timestamp", "success"]
        # Note: 'username' field in UserLoginAttempt model stores the email address
        # since email is the USERNAME_FIELD in the custom User model