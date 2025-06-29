from django.db import models
from django.db import models
from django.forms import ValidationError
from apps.users.models import User
from apps.communities.models import Community
from django.urls import reverse

class Trip(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Programmé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]

    class Meta:
        ordering = ['-temps_depart']  
        verbose_name = "Trip"          
        verbose_name_plural = "Trips"  
        indexes = [
            models.Index(fields=['statut']),
        ]
    
    conducteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips_as_driver')
    communaute = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    temps_depart = models.DateTimeField()
    temps_arrive = models.DateTimeField()
    origine = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    places_dispo = models.PositiveIntegerField()
    statut = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origine} → {self.destination} ({self.temps_depart.strftime('%d/%m/%Y %H:%M')}) - {self.conducteur.username}"
   
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
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE, related_name='reservations')
    place_reserv = models.PositiveIntegerField(default=1)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation #{self.id}: {self.passenger.username} → {self.trip} (Status: {self.statut})"
    
    def get_absolute_url(self):
        return reverse('reservation_detail', kwargs={'pk': self.pk})