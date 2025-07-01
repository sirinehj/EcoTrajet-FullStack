import pytest
from django.utils import timezone
from datetime import datetime
from unittest.mock import patch, MagicMock

# Update these imports to match your actual module paths
from user_management.serializers import CustomTokenObtainPairSerializer, UserSerializer
from user_management.models import User


# Mark this module to use the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def user_data():
    """Fixture providing test user data."""
    return {
        'email': 'test@example.com',
        'password': 'Test@1234!',
        'nom': 'Test',
        'prenom': 'User',
        'role': 'passager',
        'telephone': '1234567890'
    }


@pytest.fixture
def test_user(user_data):
    """Fixture creating and returning a test user."""
    return User.objects.create_user(
        email=user_data['email'],
        password=user_data['password'],
        nom=user_data['nom'],
        prenom=user_data['prenom'],
        role=user_data['role'],
        telephone=user_data['telephone']
    )


@pytest.fixture
def serializer_data(user_data):
    """Fixture providing basic serializer initialization data."""
    return {
        'email': user_data['email'],
        'password': user_data['password']
    }


class TestCustomTokenObtainPairSerializer:
    """Test suite for the CustomTokenObtainPairSerializer using pytest."""

    def test_validate_returns_user_data(self, serializer_data, test_user):
        """Test that validate method returns user data in the token."""
        # Create a serializer instance
        serializer = CustomTokenObtainPairSerializer(data=serializer_data)
        
        # Mock the parent class validate method
        with patch.object(CustomTokenObtainPairSerializer, 'super') as mock_super:
            # Set up the mock to return a token data dictionary
            mock_validate = MagicMock(return_value={'refresh': 'dummy_refresh', 'access': 'dummy_access'})
            mock_super.return_value.validate = mock_validate
            
            # Set the user on the serializer
            serializer.user = test_user
            
            # Call the validate method with mocked datetime
            with patch('user_management.serializers.datetime') as mock_datetime:
                mock_now = MagicMock()
                mock_now.strftime.return_value = '2025-06-30 23:48:21'
                mock_datetime.now.return_value = mock_now
                
                result = serializer.validate({})
            
            # Assertions
            mock_validate.assert_called_once_with({})
            assert 'user' in result
            assert result['user'] == UserSerializer(test_user).data
            assert 'timestamp' in result
            assert result['timestamp'] == '2025-06-30 23:48:21'
            assert 'user_login' in result
            assert result['user_login'] == test_user.email
    
    def test_validate_with_real_token(self, serializer_data, test_user):
        """Test validate with a real token rather than mocks."""
        serializer = CustomTokenObtainPairSerializer(data=serializer_data)
        assert serializer.is_valid() is True
        
        # Get the result
        result = serializer.validated_data
        
        # Verify the structure of the result
        assert 'refresh' in result
        assert 'access' in result
        assert 'user' in result
        assert 'timestamp' in result
        assert 'user_login' in result
        
        # Verify the user data
        user_data = result['user']
        assert user_data['email'] == test_user.email
        assert user_data['nom'] == test_user.nom
        assert user_data['prenom'] == test_user.prenom
        assert user_data['role'] == test_user.role
        
        # Verify the timestamp format (should be YYYY-MM-DD HH:MM:SS)
        timestamp = result['timestamp']
        # Try to parse the timestamp to verify format
        try:
            parsed_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            valid_format = True
        except ValueError:
            valid_format = False
        assert valid_format, f"Timestamp '{timestamp}' is not in the expected format"
        
        # Verify the user_login
        assert result['user_login'] == test_user.email
    
    def test_create_not_implemented(self):
        """Test that create method raises NotImplementedError."""
        serializer = CustomTokenObtainPairSerializer()
        with pytest.raises(NotImplementedError):
            serializer.create({})
    
    def test_update_not_implemented(self):
        """Test that update method raises NotImplementedError."""
        serializer = CustomTokenObtainPairSerializer()
        with pytest.raises(NotImplementedError):
            serializer.update(None, {})
    
    def test_validate_with_invalid_credentials(self, serializer_data):
        """Test validation with invalid credentials."""
        invalid_data = {
            'email': serializer_data['email'],
            'password': 'WrongPassword123!'
        }
        serializer = CustomTokenObtainPairSerializer(data=invalid_data)
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors
    
    def test_validate_with_nonexistent_user(self):
        """Test validation with a non-existent user."""
        nonexistent_user_data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        serializer = CustomTokenObtainPairSerializer(data=nonexistent_user_data)
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors