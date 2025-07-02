from django.test import TestCase
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):
    """
    Test case for the Profile model.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            nom='Test',
            prenom='User'
        )
        
    def test_profile_creation(self):
        """
        Test that a profile is automatically created when a user is created.
        """
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
        
    def test_profile_str_representation(self):
        """
        Test the string representation of a profile.
        """
        expected_str = f"{self.user.nom} {self.user.prenom}'s Profile"
        self.assertEqual(str(self.user.profile), expected_str)
        
    def test_profile_fields(self):
        """
        Test that profile fields can be updated.
        """
        profile = self.user.profile
        profile.bio = "This is a test bio"
        profile.city = "Test City"
        profile.country = "Test Country"
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        self.assertEqual(profile.bio, "This is a test bio")
        self.assertEqual(profile.city, "Test City")
        self.assertEqual(profile.country, "Test Country")