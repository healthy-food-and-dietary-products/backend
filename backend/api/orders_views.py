from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .orders_serializers import (
    OrderListSerializer,
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
)
from orders.models import Order, ShoppingCart


class ShoppingCartViewSet(ModelViewSet):
    """Viewset for ShoppingCart."""

    queryset = ShoppingCart.objects.all()
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset for Order."""

    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "delete"]

    def get_serializer_class(self):
        # if self.action in ("list", "retrieve"):
        return OrderListSerializer
        # return OrderPostDeleteSerializer # TODO for feature
