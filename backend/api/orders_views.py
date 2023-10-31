from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .orders_serializers import (
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
    OrderPostDeleteSerializer,
    OrderListSerializer
)
from orders.models import Order, ShoppingCart


class ShoppingCartViewSet(ModelViewSet):
    """Viewset for ShoppingCart."""
    queryset = ShoppingCart.objects.all()
    #
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer

        # @action(
        #     detail=True,
        #     methods=["get", "post", "patch", "delete"],
        #     permission_classes=[IsAuthenticated],
        # )
        # def shopping_cart(self, request, **kwargs):
        #     """Method for get/add/update/delete the shopping_cart."""
        # shop_cart = ShoppingCart.objects.filter(user=user).filter(status="In work")
        # if not shop_cart and request.method in ("GET", "DELETE"):
        #     return Response(
        #         "В вашей корзине нет товаров.",
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        # elif shop_cart and request.method == "POST":
        #     return Response(
        #         {
        #             "errors": "Ваша корзина еще не оформлена, "
        #             "можно добавить продукты, изменить или удалить!"
        #         }
        #     )

        # if request.method == "GET":
        #     # products = ShoppingCartProduct.objects.filter(
        #     #     shopping_cart=shop_cart.values("id"))
        #     serializer = ShoppingCartGetSerializer(
        #         data=shop_cart.values(),
        #         # products,
        #         context={'request': request})
        #     serializer.is_valid(raise_exception=True)
        #     return Response(serializer.data, status=status.HTTP_200_OK)

        # elif request.method == "DELETE":
        #     shop_cart.delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        #
        #
        #
        # def create(self, serializer):
        #     products = self.request.data["products"]
        #     serializer.save(user=self.request.user, products=products)
        # # if request.method == "POST":
        #     serializer = ShoppingCartPostUpdateDeleteSerializer(
        #         data={"products": products, "user": user},
        #         context={"request": request.data, "user": user},
        #     )
        #     serializer.is_valid(raise_exception=True)
        #     shopping_cart = ShoppingCart.objects.create(
        #         user=user,
        #         status="In work",
        #         total_price=sum(
        #             [
        #                 int(Product.objects.get(id=product["id"]).price)
        #                 * int(product["quantity"])
        #                 for product in products
        #             ]
        #         ),
        #     )
        #     ShoppingCartProduct.objects.bulk_create(
        #         [
        #             ShoppingCartProduct(
        #                 shopping_cart=shopping_cart,
        #                 quantity=product["quantity"],
        #                 product=Product.objects.get(id=product["id"]),
        #             )
        #             for product in products
        #         ]
        #     )
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)

        # elif request.method == "PATCH":
        #     serializer = ShoppingCartPostUpdateDeleteSerializer(
        #         shop_cart, data=request.data, partial=True
        #     )
        #     serializer.is_valid(raise_exception=True)
        #     return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

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
