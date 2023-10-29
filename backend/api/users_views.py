from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAuthorOrAdmin
from .users_serializers import AddressSerializer, UserAddressSerializer
from users.models import User, UserAddress


class AddressViewSet(viewsets.ModelViewSet):
    """Viewset for addresses."""

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = AddressSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """Returns a list of user addresses."""
        user = self.request.user
        return UserAddress.objects.filter(user=user)


class AddressViewSetByID(viewsets.ModelViewSet):
    """Viewset for addresses by id."""

    serializer_class = UserAddressSerializer
    permission_classes = [
        IsAuthorOrAdmin,
    ]

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        return self.get_user().user_addresses.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # TODO: fix create user_addresses
