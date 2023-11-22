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
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .mixins import DestroyWithPayloadMixin
from .orders_serializers import (
    OrderListSerializer,
    OrderPostDeleteSerializer,
    ShoppingCartSerializer,
)
from orders.models import Order
from orders.orders import NewOrder
from orders.shopping_carts import ShopCart
from products.models import Product
from users.models import User

# from .permissions import IsAuthorOrAdmin


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
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get shopping cart by id",
        operation_description=(
            "Retrieves a shopping cart of a user by its id (admin or authorized user)"
        ),
        responses={
            200: ShoppingCartSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
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
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit shopping cart",
        operation_description="Edits a shopping cart by its id (authorized only)",
        responses={
            200: ShoppingCartSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
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
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Viewset for ShoppingCart."""

    queryset = Product.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ("get", "post", "delete", "patch")
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

    def patch(self, request, **kwargs):
        shopping_cart = ShopCart(request)
        products = request.data["products"]
        serializer = ShoppingCartSerializer(data={"products": products})
        serializer.is_valid(raise_exception=True)
        for product in products:
            shopping_cart.add(
                product=product, quantity=product["quantity"], update_quantity=True
            )
        return Response(
            {
                "products": shopping_cart.__iter__(),
                "count_of_products": shopping_cart.__len__(),
                "total_price": shopping_cart.get_total_price(),
            },
            status=status.HTTP_205_RESET_CONTENT,
        )

    def delete(self, request, **kwargs):
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            return Response(
                {"errors": "no shopping_cart available"},
                status=status.HTTP_404_NOT_FOUND,
            )
        products = request.data["products"]
        for product in products:
            shopping_cart.remove(product["id"])
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
            200: "Detailed information about the deleted object and a success message",
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class OrderViewSet(ModelViewSet):
    """Viewset for Order."""

    http_method_names = ["get", "post", "delete"]
    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderListSerializer
        return OrderPostDeleteSerializer

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.get_user().orders.all()
        if self.get_user() != self.request.user:
            raise PermissionDenied()
        return self.request.user.orders.all()

    def list(self, request, **kwargs):
        if not self.request.user.is_authenticated:
            new_order = NewOrder(request)
            return Response(
                {"order": new_order.get_order_data()},
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            shopping_cart = ShopCart(request)
            if not shopping_cart:
                return Response(
                    {"errors": "no shopping_cart available"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            shopping_data = {
                "products": shopping_cart.get_shop_products(),
                "count_of_products": shopping_cart.__len__(),
                "total_price": shopping_cart.get_total_price()
            }
            new_order = NewOrder(request)

            new_order.create(shopping_data, data=request.data)
            return Response(
                {"order": new_order.get_order_data()},
                status=status.HTTP_201_CREATED,
            )
        # if self.kwargs.get("user_id") != str(self.request.user.id):
        #     raise PermissionDenied()
        return super().create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            new_order = NewOrder(request)
            new_order.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)

        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user != self.get_user() or order.user != self.request.user:
            raise PermissionDenied()
        order_restricted_deletion_statuses = [
            Order.COLLECTING,
            Order.GATHERED,
            Order.DELIVERING,
            Order.DELIVERED,
            Order.COMPLETED,
        ]
        if order.status in order_restricted_deletion_statuses:
            return Response(
                {"errors": "Отмена заказа после комплектования невозможна."}
            )
        serializer_data = self.get_serializer(order).data
        serializer_data["Success"] = "This object was successfully deleted"
        order.shopping_cart.delete()
        return Response(serializer_data, status=status.HTTP_200_OK)
