from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .permissions import IsAuthorOrAdmin
from .users_serializers import AddressSerializer
from users.models import User


class AddressViewSet(viewsets.ModelViewSet):
    """Viewset for addresses."""

    serializer_class = AddressSerializer
    permission_classes = [
        IsAuthorOrAdmin,
    ]

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        return self.get_user().addresses.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
