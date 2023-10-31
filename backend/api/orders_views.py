from rest_framework import mixins, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

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

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

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

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer
        return OrderPostDeleteSerializer
