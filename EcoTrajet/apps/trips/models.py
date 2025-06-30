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

