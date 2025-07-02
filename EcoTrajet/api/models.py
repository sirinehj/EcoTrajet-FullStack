from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from user_management.models import User
from django.urls import reverse
import uuid

class Community(models.Model):
    """
    Community model for grouping users with similar travel needs or interests.
    """
    name = models.CharField(max_length=100, help_text="Nom de la communauté")
    description = models.TextField(help_text="Description de la communauté")
    zone_geo = models.CharField(max_length=100, help_text="Zone géographique concernée")
    admin = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='admin_of',
        help_text="Administrateur de la communauté"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False, help_text="Indique si la communauté est privée")
    theme = models.CharField(max_length=50, help_text="Thème de la communauté")
    
    class Meta:
        verbose_name = 'communauté'
        verbose_name_plural = 'communautés'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Trip(models.Model):
    """
    Trip model for storing information about rides offered by drivers.
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Programmé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]

    conducteur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='trips_as_driver',
        help_text="Conducteur proposant le trajet"
    )
    communaute = models.ForeignKey(
        Community, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='trips',
        help_text="Communauté liée au trajet (optionnel)"
    )
    vehicule = models.ForeignKey(
        'user_management.Vehicule',
        on_delete=models.SET_NULL,
        null=True,
        related_name='trips',
        help_text="Véhicule utilisé pour le trajet"
    )
    temps_depart = models.DateTimeField(help_text="Date et heure de départ")
    temps_arrive = models.DateTimeField(help_text="Date et heure d'arrivée estimée")
    origine = models.CharField(max_length=100, help_text="Lieu de départ")
    destination = models.CharField(max_length=100, help_text="Lieu d'arrivée")
    prix = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Prix du trajet par passager"
    )
    places_dispo = models.PositiveIntegerField(help_text="Nombre de places disponibles")
    statut = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='SCHEDULED',
        help_text="État actuel du trajet"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'trajet'
        verbose_name_plural = 'trajets'
        ordering = ['-temps_depart']

    def __str__(self):
        return f"{self.origine} → {self.destination} ({self.temps_depart.strftime('%d/%m/%Y %H:%M')}) - {self.conducteur.email}"
   
    def get_absolute_url(self):
        return reverse('trip_detail', kwargs={'pk': self.pk})
    
    def clean(self):
        if self.places_dispo < 0:
            raise ValidationError("Le nombre de places disponibles ne peut pas être négatif !")
    
        if self.temps_arrive <= self.temps_depart:
            raise ValidationError("L'heure d'arrivée doit être après l'heure de départ !")

    def is_fully_booked(self):
        return self.places_dispo == 0

    def cancel(self):
        self.statut = 'CANCELLED'
        self.save()


class Reservation(models.Model):
    """
    Reservation model for booking seats on trips.
    """
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('CANCELLED', 'Annulé'),
    ]

    passenger = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reservations',
        help_text="Passager effectuant la réservation"
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='reservations',
        help_text="Trajet réservé"
    )
    place_reserv = models.PositiveIntegerField(
        default=1,
        help_text="Nombre de places réservées"
    )
    statut = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        help_text="État de la réservation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'réservation'
        verbose_name_plural = 'réservations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reservation #{self.id}: {self.passenger.nom} {self.passenger.prenom} → {self.trip} (Status: {self.statut})"
    
    def get_absolute_url(self):
        return reverse('reservation_detail', kwargs={'pk': self.pk})
    
    def clean(self):
        if self.place_reserv > self.trip.places_dispo:
            raise ValidationError("Le nombre de places réservées dépasse les places disponibles !")
        if self.place_reserv <= 0:
            raise ValidationError("Le nombre de places réservées doit être positif !")
        
    def save(self, *args, **kwargs):
        if self.statut == 'CONFIRMED' and self.pk:  # Only if status changed to CONFIRMED
            try:
                old_reservation = Reservation.objects.get(pk=self.pk)
                if old_reservation.statut != 'CONFIRMED':
                    self.trip.places_dispo -= self.place_reserv
                    self.trip.save()
            except Reservation.DoesNotExist:
                # First save, directly reduce places
                self.trip.places_dispo -= self.place_reserv
                self.trip.save()
        super().save(*args, **kwargs)


#Modèle pour les évaluations après trajets
class Rating(models.Model):
    """
    Rating model for user reviews after trips.
    """
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
        verbose_name = 'évaluation'
        verbose_name_plural = 'évaluations'
        # Contrainte pour éviter les doublons
        unique_together = ['reviewer', 'rated_user', 'trip']
        # Index pour les requêtes fréquentes
        indexes = [
            models.Index(fields=['rated_user', 'score']),
            models.Index(fields=['trip']),
        ]
        
    def __str__(self):
        return f"Note {self.score}/5 - {self.reviewer} -> {self.rated_user}"
    
    def clean(self):
        # Validation
        # Un utilisateur ne peut pas se noter lui-même
        if self.reviewer == self.rated_user:
            raise ValidationError("Un utilisateur ne peut pas s'auto-évaluer")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# Custom manager for Rating model
class RatingManager(models.Manager):
    """
    Custom manager for Rating model with additional calculation methods.
    """
    def average_for_user(self, user):
        """Calcule la moyenne des notes pour un utilisateur"""
        ratings = self.filter(rated_user=user)
        if ratings.exists():
            total = sum(rating.score for rating in ratings)
            return round(total / ratings.count(), 2)
        return 0
    
    def count_for_user(self, user):
        """Compte le nombre d'évaluations pour un utilisateur"""
        return self.filter(rated_user=user).count()

class Rating(models.Model):
    """
    Rating model for user reviews after trips.
    """
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
    
    # Add the managers properly:
    objects = models.Manager()  # Keep the default manager
    ratings = RatingManager()   # Add your custom manager as a second manager
    
    class Meta:
        db_table = 'rating'
        verbose_name = 'évaluation'
        verbose_name_plural = 'évaluations'
        # Contrainte pour éviter les doublons
        unique_together = ['reviewer', 'rated_user', 'trip']
        # Index pour les requêtes fréquentes
        indexes = [
            models.Index(fields=['rated_user', 'score']),
            models.Index(fields=['trip']),
        ]
        
    def __str__(self):
        return f"Note {self.score}/5 - {self.reviewer} -> {self.rated_user}"
    
    def clean(self):
        # Validation
        # Un utilisateur ne peut pas se noter lui-même
        if self.reviewer == self.rated_user:
            raise ValidationError("Un utilisateur ne peut pas s'auto-évaluer")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)