from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Власник або читання."""

    def has_object_permission(self, request, view, obj) -> bool:
        """Перевірка об'єкта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff
