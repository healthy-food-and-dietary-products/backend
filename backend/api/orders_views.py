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

from .mixins import MESSAGE_ON_DELETE, DestroyWithPayloadMixin
from .orders_serializers import (
    OrderListSerializer,
    OrderPostDeleteSerializer,
    ShoppingCartSerializer,
)
from .products_views import STATUS_200_RESPONSE_ON_DELETE_IN_DOCS
from orders.models import Delivery, Order, OrderProduct, ShoppingCart
from orders.orders import NewOrder
from orders.shopping_carts import ShopCart
from products.models import Product


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="Retrieve a shopping cart",
        operation_description="Returns a shopping cart of a user via session",
        responses={200: "List of products in the cart, quantity and total price"},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Post and edit products in a shopping cart",
        operation_description=(
            "Adds new products to the shopping cart or edits the number of products "
            "already in the shopping cart (zero is not allowed)"
        ),
        responses={
            201: "List of products in the cart, quantity and total price",
            400: ValidationErrorResponseSerializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Remove product from shopping cart",
        operation_description="Removes a product from the shopping cart using its id",
        responses={205: "No response body", 404: ErrorResponse404Serializer},
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
            product["product_id"] for product in shopping_cart.get_shop_products()
        ]
        if product_id not in products:
            return Response(
                {"errors": "Такого товара нет в корзине!"},
                status=status.HTTP_404_NOT_FOUND,
            )
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
            200: OrderListSerializer,
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
            200: OrderListSerializer,
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
            201: OrderPostDeleteSerializer,
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
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class OrderViewSet(
    DestroyWithPayloadMixin,
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
            return OrderListSerializer
        return OrderPostDeleteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.get_user().orders.all()
        return self.request.user.orders.all()

    def list(self, request, **kwargs):
        if not self.request.user.is_authenticated:
            new_order = NewOrder(request)
            return Response(
                {"order": new_order.get_order_data()}, status=status.HTTP_200_OK
            )
        serializer = self.get_serializer()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, **kwargs):
        if self.request.user.is_authenticated:
            return self.request.user.orders.filter(
                status
                in (
                    "Ordered",
                    "In processing",
                    "Collecting",
                    "Gathered",
                    "In delivering",
                    "Delivered",
                )
            )
        new_order = NewOrder(request)
        return Response(
            {"order": new_order.get_order_data()}, status=status.HTTP_200_OK
        )

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
        if not self.request.user.is_authenticated:
            new_order = NewOrder(request)

            new_order.create(shopping_data, data=request.data)
            shopping_cart.clear()
            return Response(
                {"order": new_order.get_order_data()},
                status=status.HTTP_201_CREATED,
            )

        serializer = self.get_serializer(shopping_data, request.data)
        serializer.is_valid(raise_exception=True)
        comment = None
        address = None
        if "comment" in request.data:
            comment = request.data["comment"]
        if "address" in request.data:
            address = request.data["address"]
        delivery = Delivery.objects.get(id=request.data.get("delivery_point"))
        order = Order.objects.create(
            user=self.request.user,
            status=Order.ORDERED,
            payment_method=request.data["payment_method"],
            delivery_method=request.data["delivery_method"],
            delivery_point=delivery,
            package=request.data["package"],
            comment=comment,
            address=address,
        )

        products = [
            OrderProduct.objects.create(
                product=Product.objects.get(id=prod["product_id"]),
                quantity=prod["quantity"],
                order=order,
            )
            for prod in shopping_data["products"]
        ]
        Order.products = products
        shopping_cart.clear()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        order_restricted_deletion_statuses = [
            Order.COLLECTING,
            Order.GATHERED,
            Order.DELIVERING,
            Order.DELIVERED,
            Order.COMPLETED,
        ]
        if not self.request.user.is_authenticated:
            new_order = NewOrder(request)
            if new_order.status in order_restricted_deletion_statuses:
                return Response(
                    {"errors": "Отмена заказа после комплектования невозможна."}
                )
            new_order.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)

        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user != self.get_user() or order.user != self.request.user:
            raise PermissionDenied()

        if order.status in order_restricted_deletion_statuses:
            return Response(
                {"errors": "Отмена заказа после комплектования невозможна."}
            )
        serializer_data = self.get_serializer(order).data
        serializer_data["Success"] = MESSAGE_ON_DELETE
        order.shopping_cart.delete()
        return Response(serializer_data, status=status.HTTP_200_OK)
