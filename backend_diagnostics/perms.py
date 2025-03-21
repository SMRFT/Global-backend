from rest_framework import permissions

class HasRoleAndDataPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        if ("Authorization" in request.headers.keys()):
            return True
        return False