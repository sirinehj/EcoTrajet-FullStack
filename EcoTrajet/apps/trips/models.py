import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User
from apps.communities.models import Community

class Trip(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Programmé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips_as_driver')
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE, related_name='reservations')
    seats_reserved = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

#Modèle pour les évaluations après trajets
class Rating(models.Model):
    idRate = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_ratings',
        help_text="Utilisateur qui donne la note"
    )
    rated_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_ratings',
        help_text="Utilisateur qui reçoit la note"
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text="Trajet concerné par l'évaluation"
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Note de 1 à 5 étoiles"
    )
    commentaires = models.TextField(
        blank=True,
        help_text="Commentaire optionnel"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rating'
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        # Contrainte pour éviter les doublons
        unique_together = ['reviewer', 'rated_user', 'trip']
        # Index pour les requêtes fréquentes
        indexes = [
            models.Index(fields=['rated_user', 'score'])
        ]
        models.Index(fields=['trip']),
        
    def __str__(self):
        return f"Note {self.score}/5 - {self.reviewer} -> {self.rated_user}"
    
    def clean(self):
        #Validation
        from django.core.exceptions import ValidationError
        
        # Un utilisateur ne peut pas se noter lui-même
        if self.reviewer == self.rated_user:
            raise ValidationError("Un utilisateur ne peut pas s'auto-évaluer")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
#Manager personnalisé pour les calculs de ratings
class RatingManager(models.Manager):
    
    #Calcule la moyenne des notes pour un utilisateur
    def average_for_user(self, user):
        ratings = self.filter(rated_user=user)
        if ratings.exists():
            total = sum(rating.score for rating in ratings)
            return round(total / ratings.count(), 2)
        return 0
    
    #Compte le nombre d'évaluations pour un utilisateur
    def count_for_user(self, user):
        return self.filter(rated_user=user).count()

# Ajouter le manager personnalisé au modèle Rating
Rating.add_to_class('objects', RatingManager())

