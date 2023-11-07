from django.core.exceptions import PermissionDenied
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

    # TODO: если при создании корзины ввести id другого пользователя,
    # корзина все равно создастся у меня, нужно, чтобы в этом случае была
    # ошибка типа "detail": "У вас недостаточно прав для выполнения данного действия."
    # (такую ошибку обычно выдает сработавший permission)

    # TODO: невозможно отредактировать собственную корзину методом PATCH,
    # ошибка AssertionError: The `.update()` method does not support writable nested
    # fields by default. Write an explicit `.update()` method for serializer
    # `api.orders_serializers.ShoppingCartPostUpdateDeleteSerializer`, or set
    # `read_only=True` on nested serializer fields.

    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ("get", "post", "delete", "patch")

    def get_queryset(self, **kwargs):
        user_id = self.kwargs.get("user_id")
        user = self.request.user
        if user.is_authenticated and user.id == int(user_id):
            return ShoppingCart.objects.filter(user=user)
        if user.is_admin:
            return ShoppingCart.objects.filter(user=user_id)
        raise PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer

    def get_shopping_cart(self):
        return ShoppingCart.objects.filter(user=self.request.user).filter(
            status=ShoppingCart.INWORK
        )

    def create(self, request, *args, **kwargs):
        if self.get_shopping_cart():
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
            total_price=sum(
                [
                    Product.objects.get(id=product["id"]).final_price
                    * product["quantity"]
                    for product in products
                ]
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

    def patch(self, request, *args, **kwargs):
        shopping_cart = self.get_shopping_cart()
        serializer = self.get_serializer(shopping_cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        shopping_cart = self.get_shopping_cart()
        if not shopping_cart:
            return Response(
                "В вашей корзине нет товаров.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset for Order."""

    queryset = Order.objects.all()
    permission_classes = [
        IsAuthorOrAdmin,
    ]
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
            return self.request.user.orders.all()
        return Response(
            {
                "errorrs": "Создание заказа доступно "
                "только авторизированному пользователю."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderListSerializer
        return OrderPostDeleteSerializer

    def delete(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        if order.values("status") in ("In delivering", "Delivered", "Completed"):
            Response(
                {"errors": "Отмена заказа невозможна, только отказ при получении."}
            )
        if not order:
            return Response(
                "У вас нет неисполненных заказов.", status=status.HTTP_400_BAD_REQUEST
            )
        order.delete()
        return Response("Заказ успешно удален.", status=status.HTTP_204_NO_CONTENT)
