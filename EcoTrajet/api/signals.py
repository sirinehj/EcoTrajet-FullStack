from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vehicule
from .models import Rating


@receiver(post_save, sender=Vehicule)
def vehicule_created(sender, instance, created, **kwargs):
    #Signal déclenché à la création d'un véhicule
    if created:
        print(f"Nouveau véhicule créé: {instance}")
@receiver(post_save, sender=Rating)
def rating_created(sender, instance, created, **kwargs):
    #ignal déclenché à la création d'une évaluation
    if created:
        #Notification
        print(f"Nouvelle évaluation: {instance.score}/5 pour {instance.rated_user}")
        

