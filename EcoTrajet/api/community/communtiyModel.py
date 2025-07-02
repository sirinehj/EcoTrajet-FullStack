from django.db import models
from user_management.models import User

class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    zone_geo = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_of_communities')
    date_creation = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    theme = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

class Membership(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Rejeté'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)