from django.urls import path
from .views import (
    TripListView,
    TripDetailView,
    ReservationListView,
    ReservationDetailView,
    TripReservationsView
)


urlpatterns = [    
    #Trip&Reservation
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:trip_id>/reservations/', TripReservationsView.as_view(), name='trip-reservations'),
    path('reservations/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation-detail'),
    #Trip&Reservation



]