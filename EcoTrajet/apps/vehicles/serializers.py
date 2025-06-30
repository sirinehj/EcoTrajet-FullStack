from rest_framework import serializers
from .models import Vehicule

#Serializer pour les véhicules
class VehiculeSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    places_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicule
        fields = [
            'idVehicule', 'owner', 'owner_name', 'licensePlate', 
            'make', 'model', 'couleur', 'seats', 'places_disponibles',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['idVehicule', 'created_at', 'updated_at']
        
    def get_owner_name(self, obj):
        return f"{obj.owner.prenom} {obj.owner.nom}"
    
    def get_places_disponibles(self, obj):
        return obj.places_disponibles()
    
    #Validation personnalisée pour la plaque
    def validate_licensePlate(self, value):
        if not value or len(value) < 5:
            raise serializers.ValidationError("La plaque doit contenir au moins 5 caractères")
        return value.upper()

#Serializer pour la création de véhicules
class VehiculeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicule
        fields = [
            'idVehicule' ,'owner', 'licensePlate', 'make', 'model', 
            'couleur', 'seats', 'is_active'
        ]