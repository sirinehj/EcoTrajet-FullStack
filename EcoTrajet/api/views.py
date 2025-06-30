from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Trip, Reservation
from .serializers import (
    TripListSerializer,
    TripDetailSerializer,
    TripWriteSerializer,
    TripNestedSerializer,
    ReservationListSerializer,
    ReservationDetailSerializer,
    ReservationWriteSerializer,
    ReservationNestedSerializer
)

class TripListView(generics.ListCreateAPIView):
    """
    GET: List all trips
    POST: Create new trip (driver only)
    """
    queryset = Trip.objects.select_related('conducteur', 'communaute').prefetch_related('reservations')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TripWriteSerializer
        return TripListSerializer

    def perform_create(self, serializer):
        serializer.save(conducteur=self.request.user)

class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve trip details
    PUT/PATCH: Update trip (driver only)
    DELETE: Cancel trip (driver only)
    """
    queryset = Trip.objects.select_related('conducteur').prefetch_related('reservations')
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TripWriteSerializer
        return TripDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsDriverOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_destroy(self, instance):
        """Soft delete by changing status to CANCELLED"""
        instance.statut = 'CANCELLED'
        instance.save()

class IsDriverOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow drivers to edit their trips"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.conducteur == request.user

class ReservationListView(generics.ListCreateAPIView):
    """
    GET: List all reservations
    POST: Create new reservation
    """
    serializer_class = ReservationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own reservations
        return Reservation.objects.filter(
            passenger=self.request.user
        ).select_related('trip', 'passenger')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReservationWriteSerializer
        return ReservationListSerializer

    def perform_create(self, serializer):
        # Automatically set passenger to current user
        serializer.save(passenger=self.request.user)

class ReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve reservation details
    PATCH: Update reservation status
    DELETE: Cancel reservation
    """
    queryset = Reservation.objects.select_related('trip', 'passenger')
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return ReservationWriteSerializer
        return ReservationDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsPassengerOrDriver()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        """Handle seat availability when cancelling"""
        if instance.statut == 'CONFIRMED':
            instance.trip.places_dispo += instance.place_reserv
            instance.trip.save()
        instance.delete()

class IsPassengerOrDriver(permissions.BasePermission):
    """Allow passengers to modify their reservations or drivers to modify reservations for their trips"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.passenger == request.user or obj.trip.conducteur == request.user

class TripReservationsView(generics.ListAPIView):
    """List all reservations for a specific trip (driver only)"""
    serializer_class = ReservationNestedSerializer
    permission_classes = [permissions.IsAuthenticated, IsDriverOrReadOnly]

    def get_queryset(self):
        trip_id = self.kwargs['trip_id']
        return Reservation.objects.filter(
            trip__id=trip_id
        ).select_related('passenger')