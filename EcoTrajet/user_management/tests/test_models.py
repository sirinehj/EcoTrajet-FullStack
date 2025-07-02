"""
Tests for user management models.
"""
import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from datetime import timedelta
import uuid

from user_management.models import User, UserLoginAttempt, Vehicule, UserManager


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self):
        """Test creating a user with minimal required fields."""
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        assert user.email == "test@example.com"
        assert user.nom == "Test"
        assert user.prenom == "User"
        assert user.role == "passager"  # Default role
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("Password1!")

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass1!",
            nom="Admin",
            prenom="User"
        )
        assert admin.email == "admin@example.com"
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == "admin"

    def test_user_str_representation(self):
        """Test the string representation of a user."""
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        assert str(user) == "Test User (test@example.com)"

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        User.objects.create_user(
            email="duplicate@example.com",
            password="Password1!",
            nom="First",
            prenom="User"
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="duplicate@example.com",
                password="Password1!",
                nom="Second",
                prenom="User"
            )

    def test_empty_email_raises_error(self):
        """Test that an empty email raises a ValueError."""
        with pytest.raises(ValueError):
            User.objects.create_user(
                email="",
                password="Password1!",
                nom="No",
                prenom="Email"
            )

    def test_last_updated_on_save(self):
        """Test that last_updated field is updated on save."""
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        
        # Store the initial last_updated value
        initial_update_time = user.last_updated
        
        # Wait a moment to ensure the timestamps will be different
        old_time = timezone.now() - timedelta(days=1)
        user.last_updated = old_time
        user.save(update_fields=['last_updated'])
        
        # Modify and save the user
        user.nom = "Updated"
        user.save()
        
        # Check that last_updated was updated
        assert user.last_updated > old_time
        assert user.last_updated != initial_update_time

    def test_role_choices(self):
        """Test that role must be one of the valid choices."""
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        
        # Test valid roles
        for role, _ in User.ROLE_CHOICES:
            user.role = role
            user.save()
            assert user.role == role
        
        # This would ideally test an invalid role, but Django doesn't validate choices at the model level
        # In a real application, this would be validated at the form or serializer level

    def test_payment_choices(self):
        """Test that payment preferences must be one of the valid choices."""
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        
        # Test valid payment methods
        for payment, _ in User.PAYMENT_CHOICES:
            user.paiement_prefere = payment
            user.save()
            assert user.paiement_prefere == payment
        
        # Test null payment is allowed
        user.paiement_prefere = None
        user.save()
        assert user.paiement_prefere is None

    def test_required_fields(self):
        """Test the required fields for User model."""
        assert User.USERNAME_FIELD == "email"
        assert set(User.REQUIRED_FIELDS) == {"nom", "prenom"}


@pytest.mark.django_db
class TestUserLoginAttemptModel:
    """Tests for the UserLoginAttempt model."""

    def test_create_login_attempt(self):
        """Test creating a login attempt record."""
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        
        login_attempt = UserLoginAttempt.objects.create(
            user=user,
            username="test@example.com",
            ip_address="127.0.0.1",
            success=True
        )
        
        assert login_attempt.user == user
        assert login_attempt.username == "test@example.com"
        assert login_attempt.ip_address == "127.0.0.1"
        assert login_attempt.success is True
        assert login_attempt.timestamp is not None

    def test_login_attempt_without_user(self):
        """Test creating a login attempt without a user (for failed logins with non-existent users)."""
        login_attempt = UserLoginAttempt.objects.create(
            username="nonexistent@example.com",
            ip_address="127.0.0.1",
            success=False
        )
        
        assert login_attempt.user is None
        assert login_attempt.username == "nonexistent@example.com"
        assert login_attempt.success is False

    def test_login_attempt_str_representation(self):
        """Test the string representation of a login attempt."""
        login_attempt = UserLoginAttempt.objects.create(
            username="test@example.com",
            ip_address="127.0.0.1",
            success=True
        )
        
        expected = f"test@example.com @ {login_attempt.timestamp}: Success"
        assert str(login_attempt) == expected
        
        # Test failed attempt
        failed_attempt = UserLoginAttempt.objects.create(
            username="test@example.com",
            ip_address="127.0.0.1",
            success=False
        )
        
        expected = f"test@example.com @ {failed_attempt.timestamp}: Fail"
        assert str(failed_attempt) == expected

    def test_login_attempt_ordering(self):
        """Test that login attempts are ordered by timestamp descending."""
        # Create login attempts with different timestamps
        UserLoginAttempt.objects.create(
            username="old@example.com",
            timestamp=timezone.now() - timedelta(days=2)
        )
        UserLoginAttempt.objects.create(
            username="newer@example.com",
            timestamp=timezone.now() - timedelta(days=1)
        )
        UserLoginAttempt.objects.create(
            username="newest@example.com"
        )
        
        attempts = UserLoginAttempt.objects.all()
        
        # First should be the newest
        assert attempts[0].username == "newest@example.com"
        # Last should be the oldest
        assert attempts[2].username == "old@example.com"


@pytest.mark.django_db
class TestVehiculeModel:
    """Tests for the Vehicule model."""

    @pytest.fixture
    def user(self):
        """Fixture for creating a user."""
        return User.objects.create_user(
            email="driver@example.com",
            password="Password1!",
            nom="Driver",
            prenom="User",
            role="conducteur"
        )

    def test_create_vehicule(self, user):
        """Test creating a vehicle."""
        vehicule = Vehicule.objects.create(
            owner=user,
            license_plate="ABC123",
            make="Toyota",
            model="Corolla",
            couleur="Blue",
            number_of_seats=5
        )
        
        assert vehicule.owner == user
        assert vehicule.license_plate == "ABC123"
        assert vehicule.make == "Toyota"
        assert vehicule.model == "Corolla"
        assert vehicule.couleur == "Blue"
        assert vehicule.number_of_seats == 5
        assert vehicule.is_active is True
        assert vehicule.idVehicule is not None
        assert isinstance(vehicule.idVehicule, uuid.UUID)

    def test_vehicule_str_representation(self, user):
        """Test the string representation of a vehicle."""
        vehicule = Vehicule.objects.create(
            owner=user,
            license_plate="ABC123",
            make="Toyota",
            model="Corolla",
            couleur="Blue",
            number_of_seats=5
        )
        
        assert str(vehicule) == "Toyota Corolla (ABC123)"

    def test_updated_at_on_save(self, user):
        """Test that updated_at field is updated on save."""
        vehicule = Vehicule.objects.create(
            owner=user,
            license_plate="ABC123",
            make="Toyota",
            model="Corolla",
            couleur="Blue",
            number_of_seats=5
        )
        
        # Store the initial updated_at value
        initial_update_time = vehicule.updated_at
        
        # Wait a moment to ensure the timestamps will be different
        old_time = timezone.now() - timedelta(days=1)
        vehicule.updated_at = old_time
        vehicule.save(update_fields=['updated_at'])
        
        # Modify and save the vehicle
        vehicule.couleur = "Red"
        vehicule.save()
        
        # Check that updated_at was updated
        assert vehicule.updated_at > old_time
        assert vehicule.updated_at != initial_update_time

    def test_places_disponibles(self, user):
        """Test the places_disponibles method."""
        vehicule = Vehicule.objects.create(
            owner=user,
            license_plate="ABC123",
            make="Toyota",
            model="Corolla",
            couleur="Blue",
            number_of_seats=5
        )
        
        assert vehicule.places_disponibles() == 5

    def test_license_plate_uniqueness(self, user):
        """Test that license plate must be unique."""
        Vehicule.objects.create(
            owner=user,
            license_plate="UNIQUE123",
            make="Toyota",
            model="Corolla",
            couleur="Blue",
            number_of_seats=5
        )
        
        with pytest.raises(IntegrityError):
            Vehicule.objects.create(
                owner=user,
                license_plate="UNIQUE123",  # Same license plate
                make="Honda",
                model="Civic",
                couleur="Red",
                number_of_seats=4
            )

    def test_number_of_seats_validation(self, user):
        """Test that number_of_seats must be between 1 and 9."""
        # Valid values
        for seats in [1, 5, 9]:
            vehicule = Vehicule.objects.create(
                owner=user,
                license_plate=f"SEAT{seats}",
                make="Toyota",
                model="Corolla",
                couleur="Blue",
                number_of_seats=seats
            )
            assert vehicule.number_of_seats == seats
        
        # Invalid values - in a real test with a form/serializer, this would raise ValidationError
        # Here we just check that the validators are attached to the field
        from django.core.validators import MinValueValidator, MaxValueValidator
        field = Vehicule._meta.get_field('number_of_seats')
        validators = field.validators
        
        min_validator = next((v for v in validators if isinstance(v, MinValueValidator)), None)
        max_validator = next((v for v in validators if isinstance(v, MaxValueValidator)), None)
        
        assert min_validator is not None
        assert min_validator.limit_value == 1
        assert max_validator is not None
        assert max_validator.limit_value == 9


@pytest.mark.django_db
class TestUserManager:
    """Tests for the UserManager."""

    def test_create_user_normalizes_email(self):
        """Test that create_user normalizes the email address."""
        email = "TEST@EXAMPLE.COM"
        user = User.objects.create_user(
            email=email,
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        assert user.email == "TEST@example.com"  # Django normalizes to capitalized local part

    def test_create_superuser_sets_required_flags(self):
        """Test that create_superuser sets is_staff and is_superuser to True."""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass1!",
            nom="Admin",
            prenom="User"
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.role == "admin"

    def test_timestamps_set_on_creation(self):
        """Test that date_joined and last_updated are set on creation."""
        before = timezone.now()
        user = User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nom="Test",
            prenom="User"
        )
        after = timezone.now()
        
        assert before <= user.date_joined <= after
        assert before <= user.last_updated <= after