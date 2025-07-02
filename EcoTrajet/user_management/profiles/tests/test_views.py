from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from profiles.models import Profile

User = get_user_model()


class UserProfileViewsTest(TestCase):
    """
    Test case for the profile views.
    """
    
    def setUp(self):
        """
        Set up test data and client.
        """
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            nom='Test',
            prenom='User',
            telephone='1234567890'
        )
        
        # Set up profile data
        self.profile = self.user.profile
        self.profile.bio = "Test bio"
        self.profile.city = "Test City"
        self.profile.country = "Test Country"
        self.profile.save()
        
        # Create another user for testing permissions
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpassword123',
            nom='Other',
            prenom='User'
        )
        
        # URLs
        self.profile_url = reverse('user-profile-detail')
        self.delete_url = reverse('user-profile-delete')
        
    def test_get_profile_authenticated(self):
        """
        Test that an authenticated user can retrieve their profile.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertEqual(response.data['nom'], 'Test')
        self.assertEqual(response.data['prenom'], 'User')
        self.assertEqual(response.data['profile']['bio'], 'Test bio')
        self.assertEqual(response.data['profile']['city'], 'Test City')
        self.assertEqual(response.data['profile']['country'], 'Test Country')
        
    def test_get_profile_unauthenticated(self):
        """
        Test that an unauthenticated user cannot retrieve a profile.
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_update_profile(self):
        """
        Test that a user can update their profile.
        """
        self.client.force_authenticate(user=self.user)
        
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
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], 'Updated')
        self.assertEqual(response.data['prenom'], 'Name')
        self.assertEqual(response.data['telephone'], '0987654321')
        self.assertEqual(response.data['profile']['bio'], 'Updated bio')
        self.assertEqual(response.data['profile']['city'], 'Updated City')
        self.assertEqual(response.data['profile']['country'], 'Updated Country')
        
        # Verify database was updated
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        
        self.assertEqual(self.user.nom, 'Updated')
        self.assertEqual(self.user.prenom, 'Name')
        self.assertEqual(self.user.telephone, '0987654321')
        self.assertEqual(self.user.profile.bio, 'Updated bio')
        self.assertEqual(self.user.profile.city, 'Updated City')
        self.assertEqual(self.user.profile.country, 'Updated Country')
        
    def test_delete_profile(self):
        """
        Test that a user can delete their profile.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify user was deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email='testuser@example.com')