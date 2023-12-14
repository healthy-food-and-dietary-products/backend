from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponsePermanentRedirect
from django.utils.decorators import method_decorator
from drf_standardized_errors.openapi_serializers import (
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ErrorResponse404Serializer,
    ValidationErrorResponseSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .mixins import MESSAGE_ON_DELETE, DestroyWithPayloadMixin
from .orders_serializers import (
    OrderCreateAnonSerializer,
    OrderCreateAuthSerializer,
    OrderGetAnonSerializer,
    OrderGetAuthSerializer,
    ShoppingCartSerializer,
)
from .products_views import STATUS_200_RESPONSE_ON_DELETE_IN_DOCS
from orders.models import Delivery, Order, OrderProduct, ShoppingCart
from orders.shopping_carts import ShopCart
from products.models import Product
from users.models import Address

SHOP_CART_ERROR_MESSAGE = "Такого товара нет в корзине."
ORDER_NUMBER_ERROR_MESSAGE = "Укажите верный номер заказа."
METHOD_ERROR_MESSAGE = "История заказов доступна только авторизованным пользователям."
SHOP_CART_ERROR = "В вашей корзине нет товаров, наполните её."
DELIVERY_ERROR_MESSAGE = "Отмена заказа после комплектования невозможна."


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
        products = [product["id"] for product in shopping_cart.get_shop_products()]
        if product_id not in products:
            return Response(
                {"errors": SHOP_CART_ERROR_MESSAGE},
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
            200: OrderGetAuthSerializer,
            401: METHOD_ERROR_MESSAGE,
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
            201: OrderCreateAuthSerializer,
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
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Viewset for Order."""

    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            if self.request.user.is_authenticated:
                return OrderGetAuthSerializer
            return OrderGetAnonSerializer
        if self.request.user.is_authenticated:
            return OrderCreateAuthSerializer
        return OrderCreateAnonSerializer

    def retrieve(self, request, **kwargs):
        user = self.request.user
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if user.is_authenticated and order.user != user:
            return Response({"errors": ORDER_NUMBER_ERROR_MESSAGE})
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, **kwargs):
        if self.request.user.is_authenticated:
            queryset = (
                Order.objects.select_related("user", "address", "delivery_point")
                .prefetch_related(
                    Prefetch(
                        "products",
                        queryset=Product.objects.prefetch_related("promotions"),
                    )
                )
                .filter(user=self.request.user)
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"errors": METHOD_ERROR_MESSAGE},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def create(self, request, *args, **kwargs):
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            return Response(
                {"errors": SHOP_CART_ERROR},
                status=status.HTTP_404_NOT_FOUND,
            )
        shopping_data = {
            "products": shopping_cart.get_shop_products(),
            "count_of_products": shopping_cart.__len__(),
            "total_price": shopping_cart.get_total_price(),
        }
        serializer = self.get_serializer(shopping_data, request.data)
        serializer.is_valid(raise_exception=True)
        comment = None
        package = 0
        address = None
        add_address = None
        user = None
        delivery = None
        user_data = None
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user_data = request.data["user_data"]
        if "comment" in request.data:
            comment = request.data["comment"]
        if "package" in request.data:
            package = request.data["package"]
        if "delivery_point" in request.data:
            delivery = Delivery.objects.get(id=request.data["delivery_point"])
        if "add_address" in request.data:
            add_address = request.data["add_address"]
            if request.user.is_authenticated:
                Address.objects.create(address=add_address, user=request.user)
        elif self.request.user.is_authenticated:
            address = Address.objects.get(id=request.data["address"])
        order = Order.objects.create(
            user=user,
            user_data=user_data,
            status=Order.ORDERED,
            payment_method=request.data["payment_method"],
            delivery_method=request.data["delivery_method"],
            delivery_point=delivery,
            package=package,
            comment=comment,
            address=address,
            add_address=add_address,
            total_price=shopping_data["total_price"] + int(package),
        )
        for prod in shopping_data["products"]:
            product = Product.objects.get(id=prod["id"])
            product.orders_number += 1
            product.save()
            OrderProduct.objects.create(
                product=product,
                quantity=prod["quantity"],
                order=order,
            )
        order.order_number = order.id
        order.save()
        shopping_cart.clear()
        response_serializer = (
            OrderGetAuthSerializer
            if self.request.user.is_authenticated
            else OrderGetAnonSerializer
        )
        response_serializer = response_serializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

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
            return Response({"errors": DELIVERY_ERROR_MESSAGE})
        response_serializer = (
            OrderGetAuthSerializer
            if self.request.user.is_authenticated
            else OrderGetAnonSerializer
        )
        serializer_data = response_serializer(order).data
        serializer_data["Success"] = MESSAGE_ON_DELETE
        order.delete()
        return Response(serializer_data, status=status.HTTP_200_OK)

    @action(
        methods=[
            "GET",
        ],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def pay(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs.get("pk"))
        if self.request.user.is_authenticated and order.user == self.request.user:
            return HttpResponsePermanentRedirect(f"/pay/{order.id}")
        raise PermissionDenied()
