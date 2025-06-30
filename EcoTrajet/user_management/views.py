"""
User authentication and account management views.

This module provides views for user authentication, registration, password management,
and account verification in a secure manner with rate limiting and proper token validation.
"""

# Standard library imports

import logging

# Standard library imports
from datetime import datetime, timedelta, timezone as py_timezone

# Django imports
from django.utils import timezone  # Django's timezone utilities
from rest_framework.views import APIView
from rest_framework.response import Response

# Django imports
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.permissions import IsAuthenticated

# Third-party imports
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, permissions, status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView


# Local imports
from .models import UserLoginAttempt
from .serializers import (
    EmailSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserLoginAttemptSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)


@method_decorator(
    ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post"
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Get client IP
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        username = request.data.get("username", "")
        password = request.data.get("password", "")

        # Check if user exists without authenticating
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = None

        # Authenticate
        user_auth = authenticate(username=username, password=password)

        # Log the attempt

        UserLoginAttempt.objects.create(
            user=user, username=username, ip_address=ip, success=user_auth is not None
        )

        # Check for too many failed attempts
        # In CustomTokenObtainPairView.post method:

        if user:
            recent_failed_attempts = UserLoginAttempt.objects.filter(
                user=user,
                success=False,
                timestamp__gte=timezone.now() - timedelta(minutes=30),
            ).count()

            print(f"Failed attempts in last 30 min: {recent_failed_attempts}")  # Debug

            if recent_failed_attempts >= 5:
                return Response(
                    {
                        "error": "Account temporarily locked due to too many failed login attempts. Try again later.",
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_login": "System",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Process the login
        return super().post(request, *args, **kwargs)


@method_decorator(
    ratelimit(key="ip", rate="10/h", method="POST", block=True), name="post"
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_login": user.username,
            }
        )


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Add timestamp and user login information
        data["timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        data["user_login"] = request.user.username

        return Response(data)


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

            # Send email with reset link
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {
                    "message": "Password reset email has been sent.",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_login": "System",
                }
            )
        except User.DoesNotExist:
            # Don't reveal user existence, but still return a success response
            return Response(
                {
                    "message": "Password reset email has been sent if the email exists.",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_login": "System",
                }
            )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response(
                    {
                        "message": "Password has been reset successfully.",
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_login": "System",
                    }
                )
            else:
                return Response(
                    {
                        "error": "Invalid token.",
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_login": "System",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {
                    "error": "Invalid reset link.",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_login": "System",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    """
    API endpoint that handles user logout by blacklisting JWT refresh tokens.

    This view invalidates the user's refresh token by adding it to the token blacklist,
    which prevents it from being used to obtain new access tokens. This effectively
    logs the user out of the system from all devices where this refresh token was used.

    Requires authentication to access.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """
        Handle POST requests for user logout.

        Blacklists the provided refresh token, preventing it from being used
        to generate new access tokens. Once blacklisted, the user will need to
        log in again to obtain new tokens.

        Args:
            request: HTTP request object containing:
                - refresh: The refresh token to blacklist in the request body

        Returns:
            Response: JSON response containing:
                - message: Success or error message
                - timestamp: Current UTC time in YYYY-MM-DD HH:MM:SS format
                - user_login: Username of the logged out user

        Status Codes:
            200: Successful logout
            400: Invalid token or other error
        """
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "message": "Logout successful",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_login": request.user.username,
                }
            )
        except (TokenError, AttributeError, TypeError) as e:
            logging.error("Token blacklist error: %s", str(e))
            return Response(
                {
                    "error": str(e),
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_login": request.user.username,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class EmailVerificationView(generics.GenericAPIView):
    """
    API endpoint that handles email verification after user registration.

    This view verifies the user's email by checking the provided token and UID.
    If valid, it activates the user account, allowing the user to log in.
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request, uid, token):
        """
        Handle GET requests for email verification.

        Args:
            request: HTTP request object
            uid: Base64 encoded user ID
            token: Verification token

        Returns:
            Response: JSON response with success or error message
        """
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                # Activate user
                user.is_active = True
                user.save()
                return Response(
                    {
                        "message": "Email verified successfully. Your account is now active.",
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_login": user.username,
                    }
                )
            else:
                return Response(
                    {
                        "error": "Invalid verification token.",
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_login": "System",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except (TypeError, ValueError, User.DoesNotExist):  # pylint: disable=no-member
            return Response(
                {
                    "error": "Invalid verification link.",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_login": "System",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# Add these new views to your existing views.py file


class PasswordChangeView(APIView):
    """
    View for changing user password.

    Requires authentication. Validates the old password and sets the new password.
    Optionally logs out the user from all sessions after password change.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data, context={"user": user})

        if serializer.is_valid():
            # Set new password
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()

            # Optional: Log activity
            # ActivityLog.objects.create(user=user, action="password_changed", ip_address=get_client_ip(request))

            # Optional: Send notification email
            # send_password_change_notification(user)

            # Optional: Invalidate all tokens for this user
            # If you're using token blacklist:
            # OutstandingToken.objects.filter(user=user).update(blacklisted=True)

            return Response(
                {
                    "message": "Password changed successfully. Please log in again with your new password."
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivityView(APIView):
    """
    View for retrieving user login activity history.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get login attempts for the user
        login_attempts = UserLoginAttempt.objects.filter(user=user).order_by(
            "-timestamp"
        )[
            :20
        ]  # Get last 20 login attempts

        serializer = UserLoginAttemptSerializer(login_attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
