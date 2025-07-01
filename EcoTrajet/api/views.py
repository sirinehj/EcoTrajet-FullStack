
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from .models import Trip, Reservation
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Rating, User
from django.db.models import Avg
from .models import Vehicule
from .serializers import (
    VehiculeSerializer, VehiculeCreateSerializer, RatingCreateSerializer, RatingSerializer, UserRatingStatsSerializer
)

#ViewSet pour la gestion des véhicules
class VehiculeViewSet(viewsets.ModelViewSet):
    queryset = Vehicule.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = VehiculeSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VehiculeCreateSerializer
        return VehiculeSerializer
    
    #Filtrage des véhicules
    def get_queryset(self):
        queryset = Vehicule.objects.all()
        
        # Filtrer par propriétaire
        owner_id = self.request.query_params.get('owner', None)
        if owner_id:
            queryset = queryset.filter(owner=owner_id)
        
         # Filtrer par statut actif
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filtrer par nombre de places minimum
        min_places = self.request.query_params.get('min_places', None)
        if min_places:
            queryset = queryset.filter(number_of_seats__gte=min_places)
            
        return queryset
    
    #Activer/désactiver un véhicule
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        vehicule = self.get_object()
        vehicule.is_active = not vehicule.is_active
        vehicule.save()
        
        return Response({
            'message': f'Véhicule {"activé" if vehicule.is_active else "désactivé"}',
            'is_active': vehicule.is_active
        })
        
    #Récupérer les véhicules de l'utilisateur connecté    
    @action(detail=False, methods=['get'])
    def my_vehicles(self, request):
        user_id = request.user.id
        vehicules = Vehicule.objects.filter(owner_id=user_id)
        serializer = self.get_serializer(vehicules, many=True)
        return Response(serializer.data)
    

#ViewSet pour la gestion des évaluations
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RatingCreateSerializer
        return RatingSerializer
    
    #Filtrage des évaluations
    def get_queryset(self):
        queryset = Rating.objects.all()
        
        # Filtrer par utilisateur évalué
        rated_user_id = self.request.query_params.get('rated_user', None)
        if rated_user_id:
            queryset = queryset.filter(rated_user=rated_user_id)
        
        # Filtrer par utilisateur évaluateur
        reviewer_id = self.request.query_params.get('reviewer', None)
        if reviewer_id:
            queryset = queryset.filter(reviewer=reviewer_id)
        
        # Filtrer par trajet
        trip_id = self.request.query_params.get('trip', None)
        if trip_id:
            queryset = queryset.filter(trip=trip_id)
        
        # Filtrer par score minimum
        min_score = self.request.query_params.get('min_score', None)
        if min_score:
            queryset = queryset.filter(score__gte=min_score)
        
        return queryset
    
    #Statistiques d'évaluation pour un utilisateur
    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        ratings = Rating.objects.filter(rated_user=user)
        
        #Calcul des statistiques
        avg_rating = ratings.aggregate(Avg('score'))['score__avg'] or 0
        total_ratings = ratings.count()
        
        # Détail par score
        ratings_detail = []
        for score in range(1, 6):
            count = ratings.filter(score=score).count()
            ratings_detail.append({
                'score': score,
                'count': count,
                'percentage': round((count / total_ratings * 100) if total_ratings > 0 else 0, 2)
            })
        
        data = {
            'user_id': user.id,
            'user_name': f"{user.first_name} {user.last_name}",
            'average_rating': round(avg_rating, 2),
            'total_ratings': total_ratings,
            'ratings_detail': ratings_detail
        }
        
        return Response(data)
    
    #Récupérer toutes les évaluations d'un trajet
    @action(detail=False, methods=['get'])
    def trip_ratings(self, request):
        trip_id = request.query_params.get('trip_id')
        if not trip_id:
            return Response(
                {'error': 'trip_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ratings = Rating.objects.filter(trip=trip_id)
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)
    
    #Créer plusieurs évaluations en une fois
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = RatingCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .serializers import (
    TripListSerializer,
    TripDetailSerializer,
    TripWriteSerializer,
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

