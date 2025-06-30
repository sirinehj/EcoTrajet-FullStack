from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculeViewSet, RatingViewSet
from rest_framework.authtoken.views import obtain_auth_token
from apps.users.views import ProfileView
from apps.users.views import ProfileView, UserCreateView

router = DefaultRouter()
router.register(r'vehicules', VehiculeViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('login/', obtain_auth_token, name='api-login'),
    path('profile/', ProfileView.as_view(), name='api-profile'),
    path('register/', UserCreateView.as_view(), name='api-register'),
    path('api/', include(router.urls)),

]
