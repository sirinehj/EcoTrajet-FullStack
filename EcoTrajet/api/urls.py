from django.urls import path
from .views import main
from rest_framework.authtoken.views import obtain_auth_token
from apps.users.views import ProfileView
from apps.users.views import ProfileView, UserCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('login/', obtain_auth_token, name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', UserCreateView.as_view(), name='register'),

]