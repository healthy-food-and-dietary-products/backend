from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from rest_framework import mixins, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .mixins import DestroyWithPayloadMixin
from .orders_serializers import (
    OrderListSerializer,
    OrderPostDeleteSerializer,
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
)
from .permissions import IsAuthorOrAdmin
from orders.models import Order, ShoppingCart, ShoppingCartProduct
from products.models import Product
from users.models import User


class ShoppingCartViewSet(DestroyWithPayloadMixin, ModelViewSet):
    """Viewset for ShoppingCart."""

    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ("get", "post", "delete", "patch")

    def get_queryset(self, **kwargs):
        user_id = self.kwargs.get("user_id")
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return ShoppingCart.objects.filter(user=user_id)
        if user.is_authenticated and user.id == int(user_id):
            return ShoppingCart.objects.filter(
                user=user).filter(status=ShoppingCart.INWORK)
        raise PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer

    def get_shopping_cart(self, **kwargs):
        shopping_cart = get_object_or_404(ShoppingCart, id=self.kwargs.get("pk"))
        if not shopping_cart:
            raise ObjectDoesNotExist
        if (
            shopping_cart.user == self.request.user
            and shopping_cart.status == ShoppingCart.INWORK
        ):
            return shopping_cart
        raise PermissionDenied()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if self.kwargs.get("user_id") != str(self.request.user.id):
            raise PermissionDenied()
        if (
            ShoppingCart.objects.filter(user=self.request.user)
            .filter(status=ShoppingCart.INWORK)
            .exists()
        ):
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
            total_price=(
                round(
                    sum(
                        [
                            (float(Product.objects.get(id=product["id"]).final_price))
                            * int(product["quantity"])
                            for product in products
                        ]
                    ),
                    2,
                )
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
        products = request.data["products"]
        serializer = self.get_serializer(shopping_cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if products is not None:
            shopping_cart.products.clear()
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
        shopping_cart.total_price = round(
            sum(
                [
                    (float(Product.objects.get(id=int(product["id"])).final_price))
                    * int(product["quantity"])
                    for product in products
                ]
            ),
            2,
        )
        shopping_cart.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        shopping_cart = self.get_shopping_cart()
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(
    DestroyWithPayloadMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset for Order."""

    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]
    http_method_names = ["get", "post", "delete"]
    pagination_class = None

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.role == "admin" or user.role == "moderator":
                return self.get_user().orders.all()
            if self.get_user() != self.request.user:
                raise PermissionDenied()
            return self.request.user.orders.all()
        raise PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderListSerializer
        return OrderPostDeleteSerializer

    def delete(self, request, *args, **kwargs):  # TODO: check all possible cases
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        order_restricted_deletion_statuses = [
            Order.COMPLETED,
            Order.GATHERED,
            Order.DELIVERING,
            Order.DELIVERED,
            Order.COMPLETED,
        ]
        if order.values("status") in order_restricted_deletion_statuses:
            Response({"errors": "Отмена заказа после комплектования невозможна."})
        if not order:
            return Response(
                "У вас нет неисполненных заказов.", status=status.HTTP_400_BAD_REQUEST
            )
        order.delete()
        return Response("Заказ успешно удален.", status=status.HTTP_204_NO_CONTENT)
