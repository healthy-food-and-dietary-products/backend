from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .mixins import DestroyWithPayloadMixin
from .permissions import IsAuthorOrAdmin
from .users_serializers import AddressSerializer
from users.models import User


class AddressViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for addresses."""

    serializer_class = AddressSerializer
    permission_classes = [
        IsAuthorOrAdmin,
    ]

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.get_user().addresses.all()
        return Response(
            {
                "errors": "Дейсствия с адресами доставки доступны "
                "только авторизированному пользователю!"
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
