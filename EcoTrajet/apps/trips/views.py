
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Rating, User
from django.db.models import Avg
from .serializers import (
    RatingCreateSerializer, RatingSerializer, UserRatingStatsSerializer
)

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