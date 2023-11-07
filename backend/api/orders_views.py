from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import DestroyWithPayloadMixin
from .orders_serializers import (
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
)
from orders.models import ShoppingCart, ShoppingCartProduct
from products.models import Product


class ShoppingCartViewSet(DestroyWithPayloadMixin, ModelViewSet):
    """Viewset for ShoppingCart."""

    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ("get", "post", "delete", "patch")

    def get_queryset(self, **kwargs):
        user_id = self.kwargs.get("user_id")
        user = self.request.user
        if user.is_authenticated and int(user.id) == int(user_id):
            return ShoppingCart.objects.filter(user=user)
        if user.is_admin:
            return ShoppingCart.objects.filter(user=user_id)
        raise PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer

    def get_shopping_cart(self, **kwargs):
        shopping_cart = get_object_or_404(ShoppingCart, id=self.kwargs.get("pk"))
        if not shopping_cart:
            raise ObjectDoesNotExist
        if (shopping_cart.user == self.request.user
                and shopping_cart.status == ShoppingCart.INWORK):
            return shopping_cart
        raise PermissionDenied()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if ShoppingCart.objects.filter(user=self.request.user).filter(
            status=ShoppingCart.INWORK
        ).exists():
            return Response(
                {
                    "errors": "Ваша корзина еще не оформлена, "
                    "можно добавить продукты, изменить или удалить."
                }
            )
        products = request.data["products"]
        serializer = self.get_serializer(
            data={"products": products, "user": self.request.user.id},
            context={"request": request.data, "user": self.request.user},
        )
        serializer.is_valid(raise_exception=True)
        shopping_cart = ShoppingCart.objects.create(
            user=self.request.user,
            total_price=(round(sum(
                [
                    (float(Product.objects.get(id=product["id"]).price))
                    * float(product["quantity"])
                    for product in products
                ]), 2)
            ),
        )
        ShoppingCartProduct.objects.bulk_create(
            [
                ShoppingCartProduct(
                    shopping_cart=shopping_cart,
                    quantity=product["quantity"],
                    product=Product.objects.get(id=product["id"]),
                )
                for product in products
            ]
        )
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        shopping_cart = self.get_shopping_cart()
        serializer = self.get_serializer(shopping_cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        shopping_cart.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        shopping_cart = self.get_shopping_cart()
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
