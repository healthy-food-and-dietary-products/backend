from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from djoser.serializers import TokenSerializer
from djoser.views import TokenCreateView as DjoserTokenCreateView
from djoser.views import TokenDestroyView as DjoserTokenDestroyView
from djoser.views import UserViewSet as DjoserUserViewSet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_standardized_errors.openapi_serializers import (
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ValidationErrorResponseSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets

from .mixins import DestroyWithPayloadMixin
from .users_serializers import AddressSerializer, CustomUserDeleteSerializer
from users.models import Address, User


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all addresses",
        operation_description="Returns a list of addresses of a user (admin only)",
        responses={
            200: AddressSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get address by id",
        operation_description="Retrieves an address of a user (admin only)",
        responses={
            200: AddressSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@extend_schema(parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH)])
class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for addresses."""

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.get_user().addresses.all()
        return Address.objects.none()


class CustomUserViewSet(DestroyWithPayloadMixin, DjoserUserViewSet):
    """Overrides DjoserUserViewSet serializer to delete a user without password."""

    def get_serializer_class(self):
        if self.action == "destroy" or (
            self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return CustomUserDeleteSerializer
        return super().get_serializer_class()


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Obtain auth token",
        operation_description="Allows to obtain a user authentication token",
        responses={
            201: TokenSerializer,
            400: ValidationErrorResponseSerializer,
        },
    ),
)
class CustomTokenCreateView(DjoserTokenCreateView):
    """Corrects /token/login/ response display in dynamic API docs."""

    pass


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Remove auth token",
        operation_description="Allows to remove a user authentication token",
        responses={
            204: "",
            401: ErrorResponse401Serializer,
        },
    ),
)
class CustomTokenDestroyView(DjoserTokenDestroyView):
    """Corrects /token/logout/ response display in dynamic API docs."""

    pass
