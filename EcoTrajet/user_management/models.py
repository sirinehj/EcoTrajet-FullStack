from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserLoginAttempt(models.Model):
    """
    Tracks all login attempts to the system for security monitoring and audit purposes.

    This model records both successful and failed login attempts, storing information
    about the user, username attempted, IP address, success status, and timestamp.
    This data can be used for security analysis, detecting brute force attacks,
    and meeting audit/compliance requirements.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    """Reference to the User if login was successful or if user exists (null for non-existent users)"""

    username = models.CharField(max_length=150)
    """The username that was used in the login attempt"""

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    """IP address from which the login attempt originated"""

    success = models.BooleanField(default=False)
    """Whether the login attempt was successful (True) or failed (False)"""

    timestamp = models.DateTimeField(auto_now_add=True)
    """When the login attempt occurred (automatically set on creation)"""

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.username} @ {self.timestamp}: {'Success' if self.success else 'Fail'}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
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
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='passager')
    trajet_prefere = models.CharField(max_length=255, blank=True, null=True)
    paiement_prefere = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UserManager()

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.email})"

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


#Modèle pour les véhicules 
class Vehicule(models.Model):
    idVehicule = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User,
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
        return f"{self.make} {self.model} ({self.license_plate})"
    
    def places_disponibles(self):  
        #Retourne le nbre de places disponible
        return self.number_of_seats
        """
        Model metadata options.
        """

        ordering = ["-timestamp"]  # Most recent attempts first
