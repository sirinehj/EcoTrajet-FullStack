from django.urls import path
from apps.users.views import ProfileView

urlpatterns = [
    path('api/profile/', ProfileView.as_view(), name='api-profile'),
]