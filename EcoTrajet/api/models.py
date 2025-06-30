from django.db import models
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from EcoTrajet.apps.trips.models import Trip
from apps.users.models import User

#Modèle pour les véhicules 
class Vehicule(models.Model):
    idVehicule = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicules',
        help_text="Propriétaire du véhicule"
    )
    license_plate = models.CharField(
        max_length=20,
        unique=True,
        help_text="Numéro de plaque d'immatriculation"
    )
    make = models.CharField(max_length=50, help_text="Marque du véhicule")
    model = models.CharField(max_length=50, help_text="Modèle du véhicule")
    couleur = models.CharField(max_length=30, help_text="Couleur du véhicule")
    number_of_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Véhicule actif pour les trajets"
    )
    
    # Champs de métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicule'
        verbose_name = 'vehicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['-created_at']
    

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"
    
    def places_disponibles(self):  
        #Retourne le nbre de places disponible
        return self.number_of_seats

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