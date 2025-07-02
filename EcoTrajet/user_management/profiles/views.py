from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import UserProfile
from .serializers import  UserProfileSerializer


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint that allows users to view and update their profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Returns the authenticated user.
        """
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve user profile with timestamp.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Add timestamp and user login information
        data["timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        data["user_login"] = request.user.email

        return Response(data)

    def update(self, request, *args, **kwargs):
        """
        Update user profile.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        data = serializer.data
        data["timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        data["user_login"] = request.user.email
        data["message"] = "Profile updated successfully."

        return Response(data)


class DeleteUserProfileView(APIView):
    """
    API endpoint that allows users to delete their account.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        """
        Delete user account.
        """
        user = request.user
        user_email = user.email  # Store email before deletion for response

        # Delete the user (this will cascade delete the profile due to OneToOneField)
        user.delete()

        return Response({
            "message": "User account deleted successfully.",
            "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_login": user_email
        }, status=status.HTTP_204_NO_CONTENT)