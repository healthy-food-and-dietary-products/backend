from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.decorators import method_decorator
from drf_standardized_errors.openapi_serializers import (
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ErrorResponse404Serializer,
    ValidationErrorResponseSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import DestroyWithPayloadMixin
from .orders_serializers import (
    OrderListSerializer,
    OrderPostDeleteSerializer,
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
)
from .permissions import IsAuthorOrAdmin
from orders.models import Order, ShoppingCart, ShoppingCartProduct
from orders.shopping_carts import ShopCart
from products.models import Product
from users.models import User

DECIMAL_PLACES_NUMBER = 2


@method_decorator(  # TODO: Response codes may be changed significantly
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all shopping carts",
        operation_description=(
            "Returns a list of all the shopping carts of a user "
            "(admin or authorized user)"
        ),
        responses={
            200: ShoppingCartGetSerializer,
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
            200: ShoppingCartGetSerializer,
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
            201: ShoppingCartPostUpdateDeleteSerializer,
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
            200: ShoppingCartPostUpdateDeleteSerializer,
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
class ShoppingCartViewSet(DestroyWithPayloadMixin, ModelViewSet):
    """Viewset for ShoppingCart."""

    queryset = ShoppingCart.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ("get", "post", "delete", "patch")

    def get_queryset(self, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return ShoppingCart.objects.filter(user=user.id)
        return ShoppingCart.objects.filter(user=user).filter(status=ShoppingCart.INWORK)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ShoppingCartGetSerializer
        return ShoppingCartPostUpdateDeleteSerializer

    def get_shopping_cart(self, **kwargs):
        try:
            shopping_cart = ShoppingCart.objects.get(user=self.request.user.id)
            if (
                shopping_cart.user == self.request.user
                and shopping_cart.status == ShoppingCart.INWORK
            ):
                return shopping_cart
            raise PermissionDenied()
        finally:
            ErrorResponse404Serializer("Корзина пуста")

    def list(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            shopping_cart = ShopCart(request)
            return Response(
                {
                    "products": shopping_cart.__iter__(),
                    "count_of_products": shopping_cart.__len__(),
                    "total_price": shopping_cart.get_total_price(),
                },
                status=status.HTTP_200_OK,
            )
        shopping_cart = self.get_shopping_cart()
        serializer = self.get_serializer(
            shopping_cart, data={"user": self.request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            shopping_cart = ShopCart(request)
            products = request.data["products"]
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

        user = self.request.user

        if (
            ShoppingCart.objects.filter(user=user.id)
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
            data={"products": products, "user": user.id},
            context={"request": request.data, "user": user},
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
                    DECIMAL_PLACES_NUMBER,
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
    def patch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            shopping_cart = ShopCart(request)
            products = request.data["products"]
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
                status=status.HTTP_201_CREATED,
            )

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
        if self.request.user.is_anonymous:
            shopping_cart = ShopCart(request)
            if not shopping_cart:
                return Response(
                    {"errors": "no shopping_cart available"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            shopping_cart.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)
        shopping_cart = self.get_shopping_cart()
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]

    def get_user(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.is_staff:
                return self.get_user().orders.all()
            if self.get_user() != self.request.user:
                raise PermissionDenied()
            return self.request.user.orders.all()
        return Order.objects.none()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderListSerializer
        return OrderPostDeleteSerializer

    def create(self, request, *args, **kwargs):
        if self.kwargs.get("user_id") != str(self.request.user.id):
            raise PermissionDenied()
        return super().create(request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
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
