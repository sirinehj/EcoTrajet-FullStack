from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from api.community.communtiyModel import Community, Membership
from user_management.models import User
from api.community.serializers.communitySerializer import CommunitySerializer


# PERMISSION HELPERS
def is_community_admin(user, community):
    return community.admin == user

class CommunityListView(generics.ListAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer

# Create Community
class CommunityCreateView(generics.CreateAPIView):
    serializer_class = CommunitySerializer
    

    def perform_create(self, serializer):
        community = serializer.save(admin=self.request.user)

        # Automatically add creator as admin member
        Membership.objects.create(
            user=self.request.user,
            community=community,
            status='ACCEPTED',
            is_admin=True
        )


# Delete Community
class CommunityDeleteView(generics.DestroyAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    

    def get_object(self):
        community = get_object_or_404(Community, pk=self.kwargs['pk'])
        if not is_community_admin(self.request.user, community):
            raise PermissionDenied("You are not the admin of this community.")
        return community


# Update Community
class CommunityUpdateView(generics.UpdateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    

    def get_object(self):
        community = get_object_or_404(Community, pk=self.kwargs['pk'])
        if not is_community_admin(self.request.user, community):
            raise PermissionDenied("You are not the admin of this community.")
        return community


#Add User to Community
class AddUserToCommunityView(generics.GenericAPIView):
    

    def post(self, request, *args, **kwargs):
        community_id = kwargs.get('community_id')

        community = get_object_or_404(Community, id=community_id)
        user = request.user

        # Check if user is already a member
        membership, created = Membership.objects.get_or_create(
            community=community,
            user=user,
            defaults={'status': 'ACCEPTED' if not community.is_private else 'PENDING'}
        )

        if not created:
            return Response(
                {"message": "You are already a member of this community."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": f"You have successfully {'requested to join' if community.is_private else 'joined'} the community '{community.name}'."
        }, status=status.HTTP_200_OK)

# 5. Remove User from Community
class RemoveUserFromCommunityView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        community_id = kwargs.get('community_id')
        user_id = request.data.get('user_id')

        community = get_object_or_404(Community, id=community_id)
        if not is_community_admin(request.user, community):
            return Response({"error": "You are not the admin of this community."},
                            status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, id=user_id)

        try:
            membership = Membership.objects.get(community=community, user=user)
            membership.delete()
            return Response({
                "message": f"{user.username} has been removed from {community.name}"
            }, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            return Response({
                "error": f"{user.username} is not a member of {community.name}"
            }, status=status.HTTP_404_NOT_FOUND)


#  Get All Users in Community
class ListCommunityMembersView(generics.ListAPIView):
    
    serializer_class = None  # You can define a MemberSerializer if needed

    def get_queryset(self):
        community_id = self.kwargs['community_id']
        community = get_object_or_404(Community, id=community_id)
        return Membership.objects.filter(community=community, status='ACCEPTED').select_related('user')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        members = [membership.user for membership in queryset]
        data = [{"id": user.id, "username": user.username} for user in members]
        return Response(data)