from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from drf_standardized_errors.openapi_serializers import (
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ErrorResponse404Serializer,
    ValidationErrorResponseSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .mixins import DestroyWithPayloadMixin
from .orders_serializers import (
    OrderCreateSerializer,
    OrderGetAnonSerializer,
    OrderGetAuthSerializer,
    OrderSerializer,
    ShoppingCartSerializer,
)
from orders.models import Delivery, Order, OrderProduct, ShoppingCart
from orders.shopping_carts import ShopCart
from products.models import Product
from users.models import Address


@method_decorator(  # TODO: Response codes may be changed significantly
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all shopping carts",
        operation_description=(
            "Returns a list of all the shopping carts of a user "
            "(admin or authorized user)"
        ),
        responses={
            200: ShoppingCartSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create shopping cart",
        operation_description="Creates a shopping cart of a user (authorized only)",
        responses={
            201: ShoppingCartSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete shopping cart",
        operation_description="Deletes a shopping cart by its id (authorized only)",
        responses={
            200: "Detailed information about the deleted object and a success message",
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class ShoppingCartViewSet(
    DestroyWithPayloadMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """Viewset for ShoppingCart."""

    queryset = ShoppingCart.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ("get", "post", "delete")
    serializer_class = ShoppingCartSerializer

    def list(self, request, **kwargs):
        shopping_cart = ShopCart(request)
        return Response(
            {
                "products": shopping_cart.__iter__(),
                "count_of_products": shopping_cart.__len__(),
                "total_price": shopping_cart.get_total_price(),
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, **kwargs):
        shopping_cart = ShopCart(request)
        products = request.data["products"]
        serializer = ShoppingCartSerializer(data={"products": products})
        serializer.is_valid(raise_exception=True)
        for product in products:
            shopping_cart.add(product=product, quantity=product["quantity"])
        return Response(
            {
                "products": shopping_cart.__iter__(),
                "count_of_products": shopping_cart.__len__(),
                "total_price": shopping_cart.get_total_price(),
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, *args, **kwargs):
        shopping_cart = ShopCart(self.request)
        if not shopping_cart:
            return Response(
                {"errors": "no shopping_cart available"},
                status=status.HTTP_404_NOT_FOUND,
            )
        product_id = int(self.kwargs["pk"])
        products = [
            product["id"] for product in shopping_cart.get_shop_products()]
        if product_id not in products:
            return Response({"errors": "Такого товара нет в корзине!"},
                            status=status.HTTP_404_NOT_FOUND)
        shopping_cart.remove(product_id)
        return Response(
            {
                "products": shopping_cart.__iter__(),
                "count_of_products": shopping_cart.__len__(),
                "total_price": shopping_cart.get_total_price(),
            },
            status=status.HTTP_205_RESET_CONTENT,
        )


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all orders",
        operation_description=(
            "Returns a list of all the orders of a user (admin or authorized user)"
        ),
        responses={
            200: OrderGetAuthSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get order by id",
        operation_description=(
            "Retrieves an order of a user by its id (admin or authorized user)"
        ),
        responses={
            200: OrderGetAuthSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create order",
        operation_description="Creates an order of a user (authorized only)",
        responses={
            201: OrderCreateSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete order",
        operation_description="Deletes an order by its id (authorized only)",
        responses={
            200: "Detailed information about the deleted object and a success message",
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class OrderViewSet(
    DestroyWithPayloadMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Viewset for Order."""

    http_method_names = ["get", "post", "delete"]
    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            if self.request.user.is_authenticated:
                return OrderGetAuthSerializer
            return OrderGetAnonSerializer
        if self.request.user.is_authenticated:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated or self.request.user.is_staff:
            return self.request.user.orders.all()
        return Response({"errors": "Чтобы посмотреть заказ, укажите номер"},
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, **kwargs):
        order = Order.objects.get(id=self.kwargs.get("pk"))
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            return Response(
                {"errors": "no shopping_cart available"},
                status=status.HTTP_204_NO_CONTENT,
            )
        shopping_data = {
            "products": shopping_cart.get_shop_products(),
            "count_of_products": shopping_cart.__len__(),
            "total_price": shopping_cart.get_total_price(),
        }
        serializer = self.get_serializer(shopping_data, request.data)
        serializer.is_valid(raise_exception=True)
        comment = None
        address = None
        user = None
        user_data = None
        delivery = None
        address_anonymous = None
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user_data = request.data["user_data"]
        if "comment" in request.data:
            comment = request.data["comment"]
        if "address" in request.data and self.request.user.is_authenticated:
            address = Address.objects.get(address=request.data["address"])
        elif "address" in request.data:
            address_anonymous = request.data["address"]
        if "delivery_point" in request.data:
            delivery = Delivery.objects.get(id=request.data["delivery_point"])
        order = Order.objects.create(
            user=user,
            user_data=user_data,
            status=Order.ORDERED,
            payment_method=request.data["payment_method"],
            delivery_method=request.data["delivery_method"],
            delivery_point=delivery,
            package=request.data["package"],
            comment=comment,
            address=address,
            address_anonymous=address_anonymous,
            total_price=shopping_data["total_price"]
        )

        products = [
            OrderProduct.objects.create(
                product=Product.objects.get(id=prod["id"]),
                quantity=prod["quantity"],
                order=order,
            )
            for prod in shopping_data["products"]
        ]
        Order.products = products
        order.order_number = order.id
        order.save()
        shopping_cart.clear()
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        order_restricted_deletion_statuses = [
            Order.COLLECTING,
            Order.GATHERED,
            Order.DELIVERING,
            Order.DELIVERED,
            Order.COMPLETED,
        ]
        if not self.request.user.is_authenticated:
            order = Order.objects.get(order_number=self.kwargs.get("pk"))
        else:
            order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user != self.request.user:
            raise PermissionDenied()

        if order.status in order_restricted_deletion_statuses:
            return Response(
                {"errors": "Отмена заказа после комплектования невозможна."}
            )
        # serializer_data = self.get_serializer(order).data
        # serializer_data["Success"] = "This object was successfully deleted"
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
