from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

class User(AbstractUser):
    ROLE_CHOICES = [
        ('PASSENGER', 'Passager'),
        ('DRIVER', 'Conducteur'),
        ('ADMIN', 'Administrateur'),
    ]
    
    PAYMENT_CHOICES = [
        ('CASH', 'Espèces'),
        ('CARD', 'Carte'),
        ('MOBILE', 'Mobile'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PASSENGER')
    payment_preference = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    phone = models.CharField(max_length=20)
    is_staff = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Hash password if it's being set/updated
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    is_driver = models.BooleanField(default=False)