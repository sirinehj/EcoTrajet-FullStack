from django.utils import timezone
from rest_framework import serializers
from .models import Trip, Reservation



class TripListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'origine', 'destination', 'temps_depart', 'prix', 'places_dispo', 'statut']

class ReservationNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'passenger', 'statut', 'place_reserv']


class TripDetailSerializer(serializers.ModelSerializer):
    conducteur = serializers.StringRelatedField()
    reservations = ReservationNestedSerializer(many=True, read_only=True)

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