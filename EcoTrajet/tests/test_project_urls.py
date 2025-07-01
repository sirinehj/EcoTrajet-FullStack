"""
Tests for project-level URLs.
"""
import pytest
from django.urls import reverse, resolve
from django.contrib import admin


class TestProjectUrls:
    """Tests for project-level URLs."""

    def test_admin_url(self):
        """Test admin URL."""
        url = reverse('admin:index')
        assert url == '/admin/'
        resolver = resolve(url)
        assert resolver.app_name == 'admin'

    def test_api_user_urls_included(self):
        """Test user management URLs are included."""
        # Test one URL from user_management to verify inclusion
        url = reverse('token_obtain_pair')
        assert url.startswith('/api/user/')
        
        # Test profile URL
        url = reverse('profile')
        assert url.startswith('/api/user/')

    # You would add similar tests for other included apps
    # For example, test_api_urls_included for the api app
    # However, we would need to know the URL names from that app