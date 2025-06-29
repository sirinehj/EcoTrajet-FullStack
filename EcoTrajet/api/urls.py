from django.urls import path
from .views import main
from rest_framework.authtoken.views import obtain_auth_token
from apps.users.views import ProfileView
from apps.users.views import ProfileView, UserCreateView


urlpatterns = [
    path('login/', obtain_auth_token, name='api-login'),
    path('profile/', ProfileView.as_view(), name='api-profile'),
    path('register/', UserCreateView.as_view(), name='api-register'),

]