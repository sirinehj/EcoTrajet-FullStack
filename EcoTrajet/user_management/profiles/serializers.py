from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Trajet, Reservation, Rating, Community

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']

class CommunitySerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'members_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_members_count(self, obj):
        return obj.members.count()

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    communities = CommunitySerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'full_name', 'phone_number', 'profile_picture',
            'music_preference', 'animal_preference', 'smoking_preference',
            'average_rating', 'communities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_rating', 'rating_count']

class TrajetSerializer(serializers.ModelSerializer):
    conducteur = UserProfileSerializer(read_only=True)
    places_occupees = serializers.ReadOnlyField()
    places_restantes = serializers.ReadOnlyField()
    
    class Meta:
        model = Trajet
        fields = [
            'id', 'conducteur', 'depart', 'arrivee', 'date_depart',
            'places_disponibles', 'places_occupees', 'places_restantes',
            'prix_par_personne', 'description', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'conducteur', 'created_at']

    def create(self, validated_data):
        # Le conducteur est défini à partir de l'utilisateur authentifié
        validated_data['conducteur'] = self.context['request'].user.profile
        return super().create(validated_data)

class TrajetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trajet
        fields = [
            'depart', 'arrivee', 'date_depart', 'places_disponibles',
            'prix_par_personne', 'description'
        ]

class ReservationSerializer(serializers.ModelSerializer):
    trajet = TrajetSerializer(read_only=True)
    passager = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'trajet', 'passager', 'status', 'message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RatingSerializer(serializers.ModelSerializer):
    evaluateur = UserProfileSerializer(read_only=True)
    evalue = UserProfileSerializer(read_only=True)
    trajet = TrajetSerializer(read_only=True)
    
    class Meta:
        model = Rating
        fields = [
            'id', 'evaluateur', 'evalue', 'trajet', 'note',
            'commentaire', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CommunityJoinSerializer(serializers.Serializer):
    community_id = serializers.IntegerField()
    
    def validate_community_id(self, value):
        try:
            Community.objects.get(id=value)
        except Community.DoesNotExist:
            raise serializers.ValidationError("Cette communauté n'existe pas.")
        return value

class TrajetSearchSerializer(serializers.Serializer):
    depart = serializers.CharField(max_length=200, required=False)
    arrivee = serializers.CharField(max_length=200, required=False)
    date_depart = serializers.DateField(required=False)
    places_min = serializers.IntegerField(min_value=1, required=False)
    prix_max = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)