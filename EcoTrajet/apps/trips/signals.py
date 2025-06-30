from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rating

@receiver(post_save, sender=Rating)
def rating_created(sender, instance, created, **kwargs):
    #ignal déclenché à la création d'une évaluation
    if created:
        #Notification
        print(f"Nouvelle évaluation: {instance.score}/5 pour {instance.rated_user}")