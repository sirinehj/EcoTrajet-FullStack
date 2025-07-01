from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone

class UserLoginAttempt(models.Model):
    """
    Tracks all login attempts to the system for security monitoring and audit purposes.

    This model records both successful and failed login attempts, storing information
    about the user, username attempted, IP address, success status, and timestamp.
    This data can be used for security analysis, detecting brute force attacks,
    and meeting audit/compliance requirements.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    """Reference to the User if login was successful or if user exists (null for non-existent users)"""
    
    username = models.CharField(max_length=150)
    """The username that was used in the login attempt"""
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    """IP address from which the login attempt originated"""
    
    success = models.BooleanField(default=False)
    """Whether the login attempt was successful (True) or failed (False)"""
    
    timestamp = models.DateTimeField(default=timezone.now)
    """When the login attempt occurred"""

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "login attempt"
        verbose_name_plural = "login attempts"

    def __str__(self):
        return f"{self.username} @ {self.timestamp}: {'Success' if self.success else 'Fail'}"


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model that uses email as the unique identifier.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email as the unique identifier instead of username.
    
    This model includes fields for user role (passenger, driver, admin), personal details,
    and preferences for travel and payment.
    """
    ROLE_CHOICES = [
        ('passager', 'Passager'),
        ('conducteur', 'Conducteur'),
        ('admin', 'Admin'),
    ]
    PAYMENT_CHOICES = [
        ('carte', 'Carte'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('virement', 'Virement'),
    ]

    idUser = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, help_text="Nom de famille de l'utilisateur")
    prenom = models.CharField(max_length=100, help_text="Prénom de l'utilisateur")
    email = models.EmailField(unique=True, help_text="Adresse email (utilisée comme identifiant)")
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='passager',
        help_text="Rôle de l'utilisateur dans le système"
    )
    trajet_prefere = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Trajet préféré de l'utilisateur"
    )
    paiement_prefere = models.CharField(
        max_length=20, 
        choices=PAYMENT_CHOICES, 
        blank=True, 
        null=True,
        help_text="Mode de paiement préféré"
    )
    telephone = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Numéro de téléphone"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indique si l'utilisateur est actif"
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Indique si l'utilisateur peut accéder à l'interface d'administration"
    )
    
    # Timestamps with explicit defaults for existing rows
    date_joined = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add
    last_updated = models.DateTimeField(default=timezone.now)  # Changed from auto_now

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UserManager()

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.email})"

    def save(self, *args, **kwargs):
        # Update last_updated on save (replaces auto_now)
        self.last_updated = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['nom', 'prenom']


class Vehicule(models.Model):
    """
    Model for storing vehicle information.
    
    This model stores information about vehicles that can be used for trips,
    including details such as make, model, color, and number of available seats.
    """
    # Changed back to AutoField from UUIDField
    idVehicule = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Rest of the fields remain the same
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicules',
        help_text="Propriétaire du véhicule"
    )
    license_plate = models.CharField(
        max_length=20,
        unique=True,
        help_text="Numéro de plaque d'immatriculation"
    )
    make = models.CharField(max_length=50, help_text="Marque du véhicule")
    model = models.CharField(max_length=50, help_text="Modèle du véhicule")
    couleur = models.CharField(max_length=30, help_text="Couleur du véhicule")
    number_of_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        help_text="Nombre de places disponibles (1-9)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Véhicule actif pour les trajets"
    )
    
    # Changed from auto_now_add/auto_now to default with timezone.now
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'vehicule'
        verbose_name = 'vehicule'
        verbose_name_plural = 'véhicules'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"
    
    def places_disponibles(self):
        """Retourne le nombre de places disponibles"""
        return self.number_of_seats
        
    def save(self, *args, **kwargs):
        # Update updated_at on save (replaces auto_now)
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)