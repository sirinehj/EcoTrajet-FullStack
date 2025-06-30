import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    licensePlate = models.CharField(
        max_length=20,
        unique=True,
        help_text="Numéro de plaque d'immatriculation"
    )
    make = models.CharField(max_length=50, help_text="Marque du véhicule")
    model = models.CharField(max_length=50, help_text="Modèle du véhicule")
    couleur = models.CharField(max_length=30, help_text="Couleur du véhicule")
    seats = models.PositiveIntegerField(
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
        return f"{self.make} {self.model} ({self.licensePlate})"
    
    def places_disponibles(self):  
        #Retourne le nbre de places disponible
        return self.seats