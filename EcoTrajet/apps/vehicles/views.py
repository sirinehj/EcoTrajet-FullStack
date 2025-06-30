from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vehicule
from .serializers import (
    VehiculeSerializer, VehiculeCreateSerializer
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
            queryset = queryset.filter(seats__gte=min_places)
            
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