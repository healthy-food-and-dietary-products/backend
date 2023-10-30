from rest_framework import permissions


# TODO: Possibly this class is not necessary
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


class IsAdmin(permissions.BasePermission):
    """Allows only admins to view objects."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
