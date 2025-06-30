from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Admin").exists()
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Manager").exists()
        )


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Employee").exists()
        )


class IsAuditor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Auditor").exists()
        )


class IsAuditLogViewer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return any(
            [
                request.user.groups.filter(name="Admin").exists(),
                request.user.groups.filter(name="Manager").exists(),
                request.user.groups.filter(name="Auditor").exists(),
            ]
        )


class IsAnyOf(BasePermission):
    def __init__(self, *perms):
        self.perms = perms

    def has_permission(self, request, view):
        return any(perm().has_permission(request, view) for perm in self.perms)
