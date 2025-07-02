from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class Community(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la communauté")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Communauté"
        verbose_name_plural = "Communautés"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    MUSIC_CHOICES = [
        ('none', 'Pas de musique'),
        ('classical', 'Classique'),
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('jazz', 'Jazz'),
        ('electronic', 'Électronique'),
        ('any', 'Tous genres'),
    ]

    ANIMAL_CHOICES = [
        ('none', 'Pas d\'animaux'),
        ('small', 'Petits animaux acceptés'),
        ('all', 'Tous animaux acceptés'),
    ]

    SMOKING_CHOICES = [
        ('non_smoker', 'Non-fumeur'),
        ('smoker', 'Fumeur'),
        ('occasional', 'Fumeur occasionnel'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Numéro de téléphone")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Photo de profil")

    # Préférences de covoiturage
    music_preference = models.CharField(
        max_length=20,
        choices=MUSIC_CHOICES,
        default='any',
        verbose_name="Préférence musicale"
    )
    animal_preference = models.CharField(
        max_length=10,
        choices=ANIMAL_CHOICES,
        default='none',
        verbose_name="Préférence animaux"
    )
    smoking_preference = models.CharField(
        max_length=15,
        choices=SMOKING_CHOICES,
        default='non_smoker',
        verbose_name="Préférence fumeur"
    )

    # Évaluation
    total_rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    # Communautés
    communities = models.ManyToManyField(Community, blank=True, related_name='members', verbose_name="Communautés")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    @property
    def average_rating(self):
        if self.rating_count > 0:
            return round(self.total_rating / self.rating_count, 1)
        return 0.0

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'pk': self.pk})

    def update_rating(self):
        ratings = Rating.objects.filter(evalue=self)
        if ratings.exists():
            self.total_rating = sum(r.note for r in ratings)
            self.rating_count = ratings.count()
        else:
            self.total_rating = 0.0
            self.rating_count = 0
        self.save()


class Trajet(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planifié'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]

    conducteur = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='trajets_conduits', verbose_name="Conducteur")
    passagers = models.ManyToManyField(UserProfile, through='Reservation', related_name='trajets_passager', verbose_name="Passagers")

    depart = models.CharField(max_length=200, verbose_name="Lieu de départ")
    arrivee = models.CharField(max_length=200, verbose_name="Lieu d'arrivée")
    date_depart = models.DateTimeField(verbose_name="Date et heure de départ")

    places_disponibles = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)], verbose_name="Places disponibles")
    prix_par_personne = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Prix par personne")

    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name="Statut")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trajet"
        verbose_name_plural = "Trajets"
        ordering = ['-date_depart']

    def __str__(self):
        return f"{self.depart} → {self.arrivee} ({self.date_depart.strftime('%d/%m/%Y')})"

    @property
    def places_occupees(self):
        return self.reservations.filter(status='confirmed').count()

    @property
    def places_restantes(self):
        return self.places_disponibles - self.places_occupees


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]

    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='reservations')
    passager = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reservations')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    message = models.TextField(blank=True, verbose_name="Message au conducteur")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        unique_together = ['trajet', 'passager']

    def __str__(self):
        return f"Réservation de {self.passager.full_name} pour {self.trajet}"


class Rating(models.Model):
    evaluateur = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='evaluations_donnees')
    evalue = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='evaluations_recues')
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='evaluations')

    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Note")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        unique_together = ['evaluateur', 'evalue', 'trajet']

    def __str__(self):
        return f"Évaluation de {self.evalue.full_name} par {self.evaluateur.full_name} ({self.note}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.evalue.update_rating()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()