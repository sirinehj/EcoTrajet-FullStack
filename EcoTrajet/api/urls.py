from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculeViewSet, RatingViewSet
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.routers import DefaultRouter

from .views import (
    TripListView,
    TripDetailView,
    ReservationListView,
    ReservationDetailView,
    TripReservationsView
)
from apps.users.views import ProfileView, UserCreateView

router = DefaultRouter()
router.register(r'vehicules', VehiculeViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', obtain_auth_token, name='api-login'),
    path('profile/', ProfileView.as_view(), name='api-profile'),
    path('register/', UserCreateView.as_view(), name='api-register'),

    path('login/', obtain_auth_token, name='login'),
    
    
    # Trip&Reservation
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:trip_id>/reservations/', TripReservationsView.as_view(), name='trip-reservations'),
    path('reservations/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation-detail'),
    # Trip&Reservation

]