from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.community.communtiyModel import Community, Membership

User = get_user_model()

class CommunityAPITests(APITestCase):

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass',
            email='admin@example.com'
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='regularpass',
            email='regular@example.com'
        )

        # URLs
        self.create_url = '/communities/communities/create/'
        self.list_url = '/communities/communities/'
        self.detail_url = lambda pk: f'/communities/communities/{pk}/'
        self.delete_url = lambda pk: f'/communities/communities/{pk}/delete/'
        self.join_url = lambda community_id: f'/communities/communities/{community_id}/join/'
        self.remove_member_url = lambda community_id: f'/communities/communities/{community_id}/remove-user/'
        self.members_url = lambda community_id: f'/communities/communities/{community_id}/members/'

    def authenticate(self, user=None):
        """Helper to authenticate as a specific user"""
        user = user or self.admin_user
        self.client.login(username=user.username, password='adminpass')
        return user

    # === TEST CREATE COMMUNITY ===
    def test_create_community_successfully(self):
        self.authenticate()
        data = {
            'name': 'New Community',
            'description': 'A new test community',
            'zone_geo': 'North',
            'theme': 'Test Theme'
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Community.objects.count(), 1)
        self.assertEqual(Membership.objects.count(), 1)
        self.assertTrue(Membership.objects.filter(user=self.admin_user, is_admin=True).exists())

    # === TEST LIST COMMUNITIES ===
    def test_list_communities_successfully(self):
        Community.objects.create(name='Community A', description='Test', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        Community.objects.create(name='Community B', description='Test', zone_geo='Zone', theme='Theme', admin=self.admin_user)

        self.authenticate()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # === TEST UPDATE COMMUNITY ===
    def test_update_community_by_admin(self):
        community = Community.objects.create(name='Old Name', description='Old Description', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        self.authenticate()

        update_data = {'name': 'Updated Name', 'description': 'Updated Description'}
        url = self.detail_url(community.id)
        response = self.client.put(url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        community.refresh_from_db()
        self.assertEqual(community.name, 'Updated Name')

    def test_update_community_denied_for_non_admin(self):
        community = Community.objects.create(name='Community 1', description='Desc', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        self.authenticate(user=self.regular_user)

        url = self.detail_url(community.id)
        response = self.client.put(url, {'name': 'Hacker Attempt'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # === TEST DELETE COMMUNITY ===
    def test_delete_community_by_admin(self):
        community = Community.objects.create(name='ToDelete', description='Desc', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        self.authenticate()
        url = self.delete_url(community.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Community.objects.filter(id=community.id).exists())

    def test_delete_community_denied_for_non_admin(self):
        community = Community.objects.create(name='ToDelete', description='Desc', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        self.authenticate(user=self.regular_user)
        url = self.delete_url(community.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # === TEST JOIN COMMUNITY ===
    def test_regular_user_can_join_public_community(self):
        community = Community.objects.create(
            name='Public Community',
            description='Open to all',
            zone_geo='Zone',
            theme='Theme',
            admin=self.admin_user,
            is_private=False
        )
        self.authenticate(user=self.regular_user)
        url = self.join_url(community.id)
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Membership.objects.filter(user=self.regular_user, community=community, status='ACCEPTED').exists())

    def test_regular_user_joins_private_community_pending_status(self):
        community = Community.objects.create(
            name='Private Community',
            description='Only invite',
            zone_geo='Zone',
            theme='Theme',
            admin=self.admin_user,
            is_private=True
        )
        self.authenticate(user=self.regular_user)
        url = self.join_url(community.id)
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Membership.objects.filter(user=self.regular_user, community=community, status='PENDING').exists())

    # === TEST REMOVE MEMBER FROM COMMUNITY ===
    def test_remove_member_from_community_by_admin(self):
        community = Community.objects.create(name='Team Alpha', description='Desc', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        member = User.objects.create_user(username='member', password='pass')
        Membership.objects.create(user=member, community=community, status='ACCEPTED')

        self.authenticate()
        url = self.remove_member_url(community.id)
        response = self.client.post(url, {'user_id': member.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Membership.objects.filter(user=member, community=community).exists())

    def test_remove_member_denied_for_non_admin(self):
        community = Community.objects.create(name='Team Beta', description='Desc', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        member = User.objects.create_user(username='member', password='pass')
        Membership.objects.create(user=member, community=community, status='ACCEPTED')

        self.authenticate(user=self.regular_user)
        url = self.remove_member_url(community.id)
        response = self.client.post(url, {'user_id': member.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # === TEST LIST MEMBERS OF COMMUNITY ===
    def test_list_community_members(self):
        community = Community.objects.create(name='Team Gamma', description='Desc', zone_geo='Zone', theme='Theme', admin=self.admin_user)
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')
        Membership.objects.create(user=user1, community=community, status='ACCEPTED')
        Membership.objects.create(user=user2, community=community, status='ACCEPTED')

        self.authenticate()
        url = self.members_url(community.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [item['username'] for item in response.data]
        self.assertIn('user1', usernames)
        self.assertIn('user2', usernames)