from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
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

urlpatterns = [
    # JWT token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User management endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "verify-email/<str:uid>/<str:token>/",
        EmailVerificationView.as_view(),
        name="verify_email",
    ),
    # New URLs
    path("change-password/", PasswordChangeView.as_view(), name="change_password"),
    path("activity/", UserActivityView.as_view(), name="user_activity"),
]
