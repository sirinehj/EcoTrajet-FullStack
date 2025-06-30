from rest_framework import serializers
from ...community.communtiyModel import Community

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'zone_geo', 'theme', 'is_private', 'admin', 'date_creation']
        read_only_fields = ['admin', 'date_creation']