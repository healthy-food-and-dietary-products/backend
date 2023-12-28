import stripe
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
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
    StripeCheckoutSessionCreateSerializer,
)
from .products_views import STATUS_200_RESPONSE_ON_DELETE_IN_DOCS
from core.loggers import logger
from orders.models import Delivery, Order, OrderProduct, ShoppingCart
from orders.shopping_carts import ShopCart
from products.models import Product
from users.models import Address

NO_SHOP_CART_ERROR_MESSAGE = "Отсутствует корзина покупок."
SHOP_CART_ERROR_MESSAGE = "Такого товара нет в корзине."
ORDER_USER_ERROR_MESSAGE = (
    "Заказ с данным номером принадлежит другому пользователю. "
    "Укажите номер вашего заказа."
)
METHOD_ERROR_MESSAGE = "История заказов доступна только авторизованным пользователям."
SHOP_CART_ERROR = "В вашей корзине нет товаров, наполните её."
DELIVERY_ERROR_MESSAGE = "Отмена заказа после комплектования невозможна."
PAY_SOMEONE_ELSE_ORDER_ERROR_MESSAGE = "Заказ №{pk} не принадлежит пользователю {user}."
PAY_ALREADY_PAID_ORDER_ERROR_MESSAGE = "Заказ №{pk} уже был оплачен."
STRIPE_SESSION_CREATE_ERROR_MESSAGE = (
    "Что-то пошло не так при создании Stripe Checkout Session."
)
SHOP_CART_CLEAR_MESSAGE = "Ваша корзина очищена, все товары из нее удалены."


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

    @swagger_auto_schema(
        method="delete",
        operation_summary="Clear shopping cart",
        operation_description=(
            "Deletes a product from a user's favorites (authorized user only)"
        ),
        responses={
            200: '{"message": ' + SHOP_CART_CLEAR_MESSAGE + "}",
            400: '{"errors": ' + SHOP_CART_ERROR + "}",
        },
    )
    # TODO: test this endpoint
    @transaction.atomic
    @action(detail=False, methods=["delete"], permission_classes=[permissions.AllowAny])
    def remove_all(self, request):
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            logger.error(SHOP_CART_ERROR)
            return Response(
                {"errors": SHOP_CART_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.clear()
        logger.info(SHOP_CART_CLEAR_MESSAGE)
        return Response({"message": SHOP_CART_CLEAR_MESSAGE}, status=status.HTTP_200_OK)

    def list(self, request, **kwargs):
        shopping_cart = ShopCart(request)
        logger.info("The user's shopping cart list was successfully received.")
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
        logger.info("The shopping cart was successfully created.")
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
            logger.error(NO_SHOP_CART_ERROR_MESSAGE)
            return Response(
                {"errors": NO_SHOP_CART_ERROR_MESSAGE},
                status=status.HTTP_404_NOT_FOUND,
            )
        product_id = int(self.kwargs["pk"])
        products = [product["id"] for product in shopping_cart.get_shop_products()]
        if product_id not in products:
            logger.error(SHOP_CART_ERROR_MESSAGE)
            return Response(
                {"errors": SHOP_CART_ERROR_MESSAGE},
                status=status.HTTP_404_NOT_FOUND,
            )
        shopping_cart.remove(product_id)
        logger.info(MESSAGE_ON_DELETE)
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

    queryset = OrderGetAuthSerializer.setup_eager_loading(Order.objects.all())
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "pay":
            return StripeCheckoutSessionCreateSerializer
        if self.request.method in permissions.SAFE_METHODS:
            if self.request.user.is_authenticated:
                return OrderGetAuthSerializer
            return OrderGetAnonSerializer
        if self.request.user.is_authenticated:
            return OrderCreateAuthSerializer
        return OrderCreateAnonSerializer

    def create_order_data_and_new_address(self, data):
        order_data = {}
        order_data["comment"] = None
        order_data["package"] = 0
        order_data["address"] = None
        order_data["add_address"] = None
        order_data["user"] = None
        order_data["delivery"] = None
        order_data["user_data"] = None
        if self.request.user.is_authenticated:
            order_data["user"] = self.request.user
        else:
            order_data["user_data"] = data["user_data"]
        if "comment" in data:
            order_data["comment"] = data["comment"]
        if "package" in data:
            order_data["package"] = data["package"]
        if "delivery_point" in data:
            order_data["delivery"] = Delivery.objects.get(id=data["delivery_point"])
        if "add_address" in data and data["delivery_method"] == Order.COURIER:
            order_data["add_address"] = data["add_address"]
            if self.request.user.is_authenticated:
                Address.objects.create(
                    address=order_data["add_address"], user=order_data["user"]
                )
        elif (
            self.request.user.is_authenticated
            and data["delivery_method"] == Order.COURIER
        ):
            order_data["address"] = Address.objects.get(id=data["address"])
        return order_data

    def retrieve(self, request, **kwargs):
        user = self.request.user
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if user.is_anonymous and order.user is not None:
            raise PermissionDenied()
        if user.is_authenticated and order.user != user:
            return Response({"errors": ORDER_USER_ERROR_MESSAGE})
        serializer = self.get_serializer(order)
        logger.info("The user's order was successfully received.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, **kwargs):
        if self.request.user.is_authenticated:
            queryset = self.get_queryset().filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            logger.info("The user's order list was successfully received.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(METHOD_ERROR_MESSAGE)
        return Response(
            {"errors": METHOD_ERROR_MESSAGE},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def create(self, request, *args, **kwargs):
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            logger.error(SHOP_CART_ERROR)
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
        order_data = self.create_order_data_and_new_address(request.data)

        order = Order.objects.create(
            user=order_data["user"],
            user_data=order_data["user_data"],
            status=Order.ORDERED,
            payment_method=request.data["payment_method"],
            delivery_method=request.data["delivery_method"],
            delivery_point=order_data["delivery"],
            package=order_data["package"],
            comment=order_data["comment"],
            address=order_data["address"],
            add_address=order_data["add_address"],
            total_price=shopping_data["total_price"] + int(order_data["package"]),
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
        logger.info("The order was successfully created.")
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
            logger.error("PermissionDenied during order creation.")
            raise PermissionDenied()

        if order.status in order_restricted_deletion_statuses:
            logger.error(DELIVERY_ERROR_MESSAGE)
            return Response({"errors": DELIVERY_ERROR_MESSAGE})
        response_serializer = (
            OrderGetAuthSerializer
            if self.request.user.is_authenticated
            else OrderGetAnonSerializer
        )
        serializer_data = response_serializer(order).data
        serializer_data["Success"] = MESSAGE_ON_DELETE
        order.delete()
        logger.info(MESSAGE_ON_DELETE)
        return Response(serializer_data, status=status.HTTP_200_OK)

    # TODO: test this endpoint
    # TODO: check this endpoint in api docs, do we need to add swagger_auto_schema?
    @action(methods=["POST"], detail=True, permission_classes=[permissions.AllowAny])
    def pay(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user is not None and order.user != self.request.user:
            return Response(
                {
                    "errors": PAY_SOMEONE_ELSE_ORDER_ERROR_MESSAGE.format(
                        pk=order.pk, user=request.user
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if order.is_paid is True:
            return Response(
                {"errors": PAY_ALREADY_PAID_ORDER_ERROR_MESSAGE.format(pk=order.pk)},
                status=status.HTTP_403_FORBIDDEN,
            )
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if settings.MODE == "dev":
            domain_url = f"http://{get_current_site(request)}/"
        else:
            domain_url = f"https://{get_current_site(request)}/"
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "rub",
                            "product_data": {
                                "name": order,
                            },
                            "unit_amount": int(order.total_price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                success_url=domain_url + "success",
                cancel_url=domain_url + "cancel",
                client_reference_id=request.user.username
                if request.user.is_authenticated
                else None,
                payment_method_types=["card"],
                mode="payment",
                metadata={"order_id": order.id},
            )
            logger.info("Stripe Checkout Session created successfully.")
            return Response(
                {"checkout_session_url": checkout_session.url},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": STRIPE_SESSION_CREATE_ERROR_MESSAGE, "errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
