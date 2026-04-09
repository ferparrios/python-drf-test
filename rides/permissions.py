from rest_framework.permissions import BasePermission

from rides.models import User


class IsAdminRole(BasePermission):
    """
    Only users with role 'admin' may access the API (per assessment).
    """

    message = "Only users with role 'admin' can access this API."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) == User.ROLE_ADMIN
