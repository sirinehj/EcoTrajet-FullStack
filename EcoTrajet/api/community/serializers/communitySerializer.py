from rest_framework import serializers
from ...community.communtiyModel import Community
from user_management.models import User
class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'zone_geo', 'theme', 'is_private','date_creation']
        read_only_fields = ['admin', 'date_creation']
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('admin', None)
        community = Community.objects.create(admin=user, **validated_data)
        community.memberships.create(user=user, status='ACCEPTED', is_admin=True)
        return community