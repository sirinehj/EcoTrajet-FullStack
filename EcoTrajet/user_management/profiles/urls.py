from django.urls import path
from .views import UserProfileDetailView, DeleteUserProfileView

urlpatterns = [
    path('', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('delete/', DeleteUserProfileView.as_view(), name='user-profile-delete'),  # Fixed typo
]