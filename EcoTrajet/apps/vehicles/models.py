from django.db import models
from apps.users.models import User

class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)  # Brand (e.g., Renault)
    model = models.CharField(max_length=50)  # Model (e.g., Clio)
    color = models.CharField(max_length=30)
    seats = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"