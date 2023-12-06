from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allows only admins to create, edit and delete objects."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Allows only the author to post/edit/delete the review."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
