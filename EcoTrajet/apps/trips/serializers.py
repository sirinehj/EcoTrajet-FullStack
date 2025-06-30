from rest_framework import serializers
from .models import Rating

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