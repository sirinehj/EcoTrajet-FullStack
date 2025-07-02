"""
Tests for user management URLs.
"""
import pytest
from django.urls import reverse, resolve
from rest_framework_simplejwt.views import TokenRefreshView

from user_management.views import (
    EmailVerificationView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    UserActivityView,
    UserProfileView,
    CustomTokenObtainPairView,
)


class TestUserManagementUrls:
    """Tests for user management URLs."""

    def test_token_obtain_pair_url(self):
        """Test token obtain pair URL."""
        url = reverse('token_obtain_pair')
        assert url == '/api/user/token/'
        resolver = resolve(url)
        assert resolver.func.view_class == CustomTokenObtainPairView

    def test_token_refresh_url(self):
        """Test token refresh URL."""
        url = reverse('token_refresh')
        assert url == '/api/user/token/refresh/'
        resolver = resolve(url)
        assert resolver.func.view_class == TokenRefreshView

    def test_register_url(self):
        """Test register URL."""
        url = reverse('register')
        assert url == '/api/user/register/'
        resolver = resolve(url)
        assert resolver.func.view_class == RegisterView

    def test_profile_url(self):
        """Test profile URL."""
        url = reverse('profile')
        assert url == '/api/user/profile/'
        resolver = resolve(url)
        assert resolver.func.view_class == UserProfileView

    def test_logout_url(self):
        """Test logout URL."""
        url = reverse('logout')
        assert url == '/api/user/logout/'
        resolver = resolve(url)
        assert resolver.func.view_class == LogoutView

    def test_password_reset_url(self):
        """Test password reset URL."""
        url = reverse('password_reset')
        assert url == '/api/user/password-reset/'
        resolver = resolve(url)
        assert resolver.func.view_class == PasswordResetRequestView

    def test_password_reset_confirm_url(self):
        """Test password reset confirm URL."""
        url = reverse('password_reset_confirm')
        assert url == '/api/user/password-reset/confirm/'
        resolver = resolve(url)
        assert resolver.func.view_class == PasswordResetConfirmView

    def test_verify_email_url(self):
        """Test email verification URL."""
        uid = 'test-uid'
        token = 'test-token'
        url = reverse('verify_email', kwargs={'uid': uid, 'token': token})
        assert url == f'/api/user/verify-email/{uid}/{token}/'
        resolver = resolve(url)
        assert resolver.func.view_class == EmailVerificationView
        assert resolver.kwargs['uid'] == uid
        assert resolver.kwargs['token'] == token

    def test_change_password_url(self):
        """Test change password URL."""
        url = reverse('change_password')
        assert url == '/api/user/change-password/'
        resolver = resolve(url)
        assert resolver.func.view_class == PasswordChangeView

    def test_user_activity_url(self):
        """Test user activity URL."""
        url = reverse('user_activity')
        assert url == '/api/user/activity/'
        resolver = resolve(url)
        assert resolver.func.view_class == UserActivityView