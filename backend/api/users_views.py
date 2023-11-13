from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.response import Response

from .mixins import DestroyWithPayloadMixin
from .permissions import IsAdmin
from .users_serializers import AddressSerializer, CustomUserDeleteSerializer
from users.models import User


class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for addresses."""

    serializer_class = AddressSerializer
    permission_classes = [IsAdmin]

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.get_user().addresses.all()
        return Response(
            {
                "errors": (
                    "Действия c адресами доставки доступны "
                    "только авторизированному пользователю."
                )
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomUserViewSet(DestroyWithPayloadMixin, DjoserUserViewSet):
    """Overrides DjoserUserViewSet serializer to delete a user without password."""

    def get_serializer_class(self):
        if self.action == "destroy" or (
            self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return CustomUserDeleteSerializer
        return super().get_serializer_class()
