from rest_framework import permissions, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .orders_serializers import (
    OrderListSerializer,
    OrderPostDeleteSerializer,
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
)
from orders.models import Order, ShoppingCart, ShoppingCartProduct
from products.models import Product


class ShoppingCartViewSet(ModelViewSet):
    """Viewset for ShoppingCart."""

    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ("get", "post", "delete", "patch")
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=self.request.user)
        return Response({"errorrs": "Просмотр корзины доступен "
                         "только авторизированному пользователю!"},
                        status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer

    def get_shopping_cart(self):
        return ShoppingCart.objects.filter(user=self.request.user).filter(
            status="In work"
        )

    def create(self, request, *args, **kwargs):
        if self.get_shopping_cart():
            return Response(
                {
                    "errors": "Ваша корзина еще не оформлена, "
                    "можно добавить продукты, изменить или удалить!"
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
            status="In work",
            total_price=sum(
                [
                    int(Product.objects.get(id=product["id"]).price)
                    * int(product["quantity"])
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "delete"]
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user.id)
        return Response({"errorrs": "Создание заказа доступно "
                         "только авторизированному пользователю!"},
                        status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderListSerializer
        return OrderPostDeleteSerializer


    def delete(self, request, *args, **kwargs):
        print(kwargs, request.data)
        order = get_object_or_404(Order, id=self.kwargs.get('order_id'))
            # Order.objects.get(user=request.user).filter(
            # id=self.kwargs["id"])
        print(order)
        if order.values("status") in ("In delivering", "Delivered", "Completed"):
            Response({"errors": "Отмена заказа невозможна,"
                                "только отказ при получении!"})
        if not order:
            return Response(
                "У вас нет неисполненных заказов.",
                status=status.HTTP_400_BAD_REQUEST
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
