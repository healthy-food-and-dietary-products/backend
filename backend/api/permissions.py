from rest_framework import permissions


class IsAuthorOnly(permissions.BasePermission):
    """Only Author has permissions."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAuthor(permissions.BasePermission):
    """Only the author has full access to its own favorite products."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allows only admins to create, edit and delete objects."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )
