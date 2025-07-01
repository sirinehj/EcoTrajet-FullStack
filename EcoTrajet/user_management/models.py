from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings


class UserLoginAttempt(models.Model):
    """
    Tracks all login attempts to the system for security monitoring and audit purposes.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

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


class Vehicule(models.Model):
    idVehicule = models.AutoField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicules')
    license_plate = models.CharField(max_length=30, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    couleur = models.CharField(max_length=30)
    number_of_seats = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"