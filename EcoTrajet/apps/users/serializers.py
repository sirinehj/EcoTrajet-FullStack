from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, UserProfile
from apps.vehicles.serializers import VehicleSerializer 
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 
                 'role', 'phone', 'payment_preference', 'is_staff', 'auth_token']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'phone': {'required': True}
        }

    def create(self, validated_data):
        # Hash password before creation
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hash password if it's being updated
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
        
    def get_auth_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key
    
class UserProfileSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['bio', 'is_driver', 'vehicles']