from django.urls import path
from api.community.communityView import (
    CommunityCreateView,
    CommunityDeleteView,
    CommunityUpdateView,
    CommunityListView,
    AddUserToCommunityView,
    RemoveUserFromCommunityView,
    ListCommunityMembersView,
)

urlpatterns = [
    path('', CommunityListView.as_view(), name='community-create'),
    path('add-community/',CommunityCreateView.as_view(),name='create-new-community'),
    path('<int:pk>/', CommunityUpdateView.as_view(), name='community-update'),
    path('<int:pk>/delete/', CommunityDeleteView.as_view(), name='community-delete'),
    path('<int:community_id>/add-user/', AddUserToCommunityView.as_view(), name='community-add-user'),
    path('<int:community_id>/remove-user/', RemoveUserFromCommunityView.as_view(), name='community-remove-user'),
    path('<int:community_id>/members/', ListCommunityMembersView.as_view(), name='community-members-list'),
]