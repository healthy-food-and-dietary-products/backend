from rest_framework import viewsets

from .users_serializers import AddressSerializer, UserCreateSerializer, UserSerializer
from users.models import Address, User


class AddressViewSet(viewsets.ModelViewSet):
    """Viewset for addresses."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    # TODO: add permissions:
    # admins see all the addresses,
    # users see their own addresses on their own profile pages
    permission_classes = []


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for users."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # TODO: add permissions:
    # admins see all the users,
    # users see their own user info
    permission_classes = []

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        # if self.action == "partial_update":
        #     return UserUpdateSerializer  # TODO: make this serializer
        return UserSerializer
