from rest_framework import serializers
from user_management.models import Vehicule
from .models import Rating
from django.utils import timezone
from rest_framework import serializers
from .models import Trip, Reservation


#Serializer pour les véhicules
class VehiculeSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    places_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicule
        fields = [
            'idVehicule', 'owner', 'owner_name', 'license_plate', 
            'make', 'model', 'couleur', 'number_of_seats', 'places_disponibles',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['idVehicule', 'created_at', 'updated_at']
        
    def get_owner_name(self, obj):
        return f"{obj.owner.prenom} {obj.owner.nom}"
    
    def get_places_disponibles(self, obj):
        return obj.places_disponibles()
    
    #Validation personnalisée pour la plaque
    def validate_license_plate(self, value):
        if not value or len(value) < 5:
            raise serializers.ValidationError("La plaque doit contenir au moins 5 caractères")
        return value.upper()

#Serializer pour la création de véhicules
class VehiculeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicule
        fields = [
            'idVehicule' ,'owner', 'license_plate', 'make', 'model', 
            'couleur', 'number_of_seats', 'is_active'
        ]
        
#Serializer pour les évaluations
class RatingSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    rated_user_name = serializers.SerializerMethodField()
    trip_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Rating
        fields = [
            'idRate', 'reviewer', 'reviewer_name', 'rated_user', 
            'rated_user_name', 'trip', 'trip_info', 'score', 
            'commentaires', 'created_at'
        ]
        read_only_fields = ['idRate', 'created_at']
    
    def get_reviewer_name(self, obj):
        return f"{obj.reviewer.prenom} {obj.reviewer.nom}"
    
    def get_rated_user_name(self, obj):
        return f"{obj.rated_user.prenom} {obj.rated_user.nom}"
    
    def get_trip_info(self, obj):
        if obj.trip:
            return f"{obj.trip.origin} -> {obj.trip.destination}"
        return None
    
#Serializer pour la création d'évaluations
class RatingCreateSerializer(serializers.ModelSerializer):
    #Champ commentaires optionnel
    commentaires = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Rating
        fields = ['reviewer', 'rated_user', 'trip', 'score', 'commentaires']
        
    #Validation
    def validate(self, data):
        if data['reviewer'] == data['rated_user']:
            raise serializers.ValidationError("Un utilisateur ne peut pas s'auto-évaluer")
        if Rating.objects.filter(
            reviewer=data['reviewer'],
            rated_user=data['rated_user'],
            trip=data['trip']
        ).exists():
            raise serializers.ValidationError("Vous avez déjà évalué cet utilisateur pour ce trajet.")
        return data
#Serializer pour les statistiques d'évaluation d'un utilisateur
class UserRatingStatsSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    user_name = serializers.CharField()
    average_rating = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    ratings_detail = serializers.ListField()

class TripListSerializer(serializers.ModelSerializer):
    conducteur = serializers.SerializerMethodField()
    class Meta:
        model = Trip
        fields = ['id', 'conducteur', 'temps_depart', 'temps_arrive', 'origine', 'destination', 'prix', 'places_dispo']

    def get_conducteur(self, obj):
        return {
            'id': obj.conducteur.idUser,
            'prenom': obj.conducteur.prenom,
            'nom': obj.conducteur.nom,
            'email': obj.conducteur.email
        }
    
class ReservationNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'passenger', 'statut', 'place_reserv']


class TripDetailSerializer(serializers.ModelSerializer):
    conducteur = serializers.StringRelatedField()
    reservation = ReservationNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['created_at', 'conducteur']


class TripWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating trips"""
    class Meta:
        model = Trip
        fields = '__all__'
        extra_kwargs = {
            'conducteur': {'read_only': True},
            'statut': {'read_only': True}
        }

    def validate_temps_depart(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("La date de départ ne peut pas être dans le passé")
        return value

    def validate(self, data):
        # Replicates model's clean() method
        if 'temps_arrive' in data and 'temps_depart' in data:
            if data['temps_arrive'] <= data['temps_depart']:
                raise serializers.ValidationError(
                    "L'heure d'arrivée doit être après l'heure de départ"
                )
        
        if 'places_dispo' in data and data['places_dispo'] < 0:
            raise serializers.ValidationError(
                "Le nombre de places disponibles ne peut pas être négatif"
            )
            
        return data

class TripNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'origine', 'destination', 'temps_depart']


class ReservationListSerializer(serializers.ModelSerializer):
    passenger = serializers.StringRelatedField()
    trip = TripNestedSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'passenger', 'trip', 'place_reserv', 'statut', 'created_at']

class ReservationDetailSerializer(serializers.ModelSerializer):
    passenger = serializers.StringRelatedField()
    trip = TripDetailSerializer()  # Or TripListSerializer for less detail

    class Meta:
        model = Reservation
        fields = '__all__'

class ReservationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        exclude = ['created_at']
