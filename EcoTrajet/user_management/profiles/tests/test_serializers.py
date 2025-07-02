from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from profiles.models import Profile
from profiles.serializers import ProfileSerializer, UserProfileSerializer

User = get_user_model()


class ProfileSerializerTest(TestCase):
    """
    Test case for the ProfileSerializer.
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
        self.profile = self.user.profile
        self.profile.bio = "Test bio"
        self.profile.city = "Test City"
        self.profile.save()
        
    def test_profile_serializer(self):
        """
        Test that the ProfileSerializer correctly serializes a Profile instance.
        """
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        
        self.assertEqual(data['bio'], "Test bio")
        self.assertEqual(data['city'], "Test City")
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)


class UserProfileSerializerTest(TestCase):
    """
    Test case for the UserProfileSerializer.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            nom='Test',
            prenom='User',
            telephone='1234567890'
        )
        self.profile = self.user.profile
        self.profile.bio = "Test bio"
        self.profile.city = "Test City"
        self.profile.save()
        
        self.factory = APIRequestFactory()
        
    def test_user_profile_serializer(self):
        """
        Test that the UserProfileSerializer correctly serializes a User instance with its Profile.
        """
        serializer = UserProfileSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], 'testuser@example.com')
        self.assertEqual(data['nom'], 'Test')
        self.assertEqual(data['prenom'], 'User')
        self.assertEqual(data['telephone'], '1234567890')
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['bio'], 'Test bio')
        self.assertEqual(data['profile']['city'], 'Test City')
        
    def test_user_profile_update(self):
        """
        Test that the UserProfileSerializer correctly updates a User instance and its Profile.
        """
        update_data = {
            'nom': 'Updated',
            'prenom': 'Name',
            'telephone': '0987654321',
            'profile': {
                'bio': 'Updated bio',
                'city': 'Updated City',
                'country': 'Updated Country'
            }
        }
        
        serializer = UserProfileSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        
        # Refresh from database
        updated_user.refresh_from_db()
        updated_user.profile.refresh_from_db()
        
        self.assertEqual(updated_user.nom, 'Updated')
        self.assertEqual(updated_user.prenom, 'Name')
        self.assertEqual(updated_user.telephone, '0987654321')
        self.assertEqual(updated_user.profile.bio, 'Updated bio')
        self.assertEqual(updated_user.profile.city, 'Updated City')
        self.assertEqual(updated_user.profile.country, 'Updated Country')