from rest_framework import permissions


class IsAuthorOnly(permissions.BasePermission):
    """Only Author has permissions."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
