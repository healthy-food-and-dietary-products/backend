from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.validators import ValidationError
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
        queryset = self.get_queryset()
        priority_count = queryset.filter(priority_address=True).count()
        if priority_count == 1:
            raise ValidationError('Нельзя выбрать более одного приоритетного адреса.')
        
        serializer.save(user=self.request.user)
