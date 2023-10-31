from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .orders_serializers import (
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
)
from .users_serializers import AddressSerializer, UserCreateSerializer, UserSerializer
from orders.models import ShoppingCart, ShoppingCartProduct
from products.models import Product
from users.models import Address, User


class AddressViewSet(viewsets.ModelViewSet):
    """Viewset for addresses."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    # TODO: add permissions:
    # admins see all the addresses,
    # users see their own addresses on their own profile pages
    permission_classes = []


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for users."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # TODO: add permissions:
    # admins see all the users,
    # users see their own user info
    permission_classes = []

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        # if self.action == "partial_update":
        #     return UserUpdateSerializer  # TODO: make this serializer
        return UserSerializer

    @action(
        detail=True,
        methods=["get", "post", "patch", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        """Method for get/add/update/delete the shopping_cart."""

        user = request.user
        if str(user.id) != str(self.kwargs["pk"]):
            return Response(status=status.HTTP_403_FORBIDDEN)
        shop_cart = ShoppingCart.objects.filter(user=user).filter(status="In work")
        if not shop_cart and request.method in ("GET", "DELETE"):
            return Response(
                "В вашей корзине нет товаров.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif shop_cart and request.method == "POST":
            return Response(
                {
                    "errors": "Ваша корзина еще не оформлена, "
                    "можно добавить продукты, изменить или удалить!"
                }
            )

        if request.method == "GET":
            serializer = ShoppingCartGetSerializer(shop_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            shop_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        products = request.data["products"]
        if request.method == "POST":
            serializer = ShoppingCartPostUpdateDeleteSerializer(
                data={"products": products, "user": user},
                context={"request": request.data, "user": user},
            )
            serializer.is_valid(raise_exception=True)
            shopping_cart = ShoppingCart.objects.create(
                user=user,
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

        elif request.method == "PATCH":
            serializer = ShoppingCartPostUpdateDeleteSerializer(
                shop_cart, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
