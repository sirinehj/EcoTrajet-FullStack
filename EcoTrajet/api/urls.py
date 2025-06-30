from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from apps.users.views import ProfileView
from apps.users.views import ProfileView, UserCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    TripListView,
    TripDetailView,
    ReservationListView,
    ReservationDetailView,
    TripReservationsView
)

urlpatterns = [

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('login/', obtain_auth_token, name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', UserCreateView.as_view(), name='register'),
    
    #Trip&Reservation
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:trip_id>/reservations/', TripReservationsView.as_view(), name='trip-reservations'),
    path('reservations/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation-detail'),
    #Trip&Reservation



]
