# user_management/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Admin'

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Manager'

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Employee'

class IsAuditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Auditor'

class IsAuditLogViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['Admin', 'Manager', 'Auditor']

class IsAnyOf(permissions.BasePermission):
    def __init__(self, *permission_classes):
        self.permission_classes = permission_classes

    def has_permission(self, request, view):
        return any(
            permission_class().has_permission(request, view)
            for permission_class in self.permission_classes
        )