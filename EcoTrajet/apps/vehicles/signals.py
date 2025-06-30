from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vehicule

@receiver(post_save, sender=Vehicule)
def vehicule_created(sender, instance, created, **kwargs):
    #Signal déclenché à la création d'un véhicule
    if created:
        print(f"Nouveau véhicule créé: {instance}")