import stripe
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_standardized_errors.openapi_serializers import (
    ClientErrorEnum,
    ErrorCode401Enum,
    ErrorCode403Enum,
    ErrorCode404Enum,
    ErrorCode406Enum,
    ErrorCode500Enum,
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ErrorResponse404Serializer,
    ErrorResponse406Serializer,
    ErrorResponse500Serializer,
    ServerErrorEnum,
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
    ShoppingCartListSerializer,
    ShoppingCartRemoveAllSerializer,
    ShoppingCartSerializer,
    StripeCheckoutSessionCreateSerializer,
    StripePaySuccessPageSerializer,
    StripeSessionCreateSerializer,
)
from .products_serializers import CouponSerializer
from .products_views import STATUS_200_RESPONSE_ON_DELETE_IN_DOCS
from core.loggers import logger
from core.utils import generate_order_number
from orders.models import Delivery, Order, OrderProduct, ShoppingCart
from orders.shopping_carts import ShopCart
from products.models import Coupon, Product
from users.models import Address

NO_SHOP_CART_ERROR_MESSAGE = "Отсутствует корзина покупок."
SHOP_CART_ERROR_MESSAGE = "Такого товара нет в корзине."
ORDER_USER_ERROR_MESSAGE = (
    "Заказ с данным номером принадлежит другому пользователю. "
    "Укажите номер вашего заказа."
)
METHOD_ERROR_MESSAGE = "История заказов доступна только авторизованным пользователям."
SHOP_CART_ERROR = "В вашей корзине нет товаров, наполните её."
DELETE_ORDER_WITH_RESTRICTED_STATUS_ERROR_MESSAGE = (
    "Отмена заказа после начала комплектования невозможна."
)
DELETE_ORDER_BY_ANONYMOUS_ERROR_MESSAGE = (
    "Отмена заказа анонимным пользователем невозможна."
)
PAY_SOMEONE_ELSE_ORDER_ERROR_MESSAGE = "Заказ №{pk} не принадлежит пользователю {user}."
PAY_ALREADY_PAID_ORDER_ERROR_MESSAGE = "Заказ №{pk} уже был оплачен."
STRIPE_SESSION_CREATE_ERROR_MESSAGE = "Ошибка создания Stripe Checkout Session."
STRIPE_INVALID_SESSION_ID_ERROR_MESSAGE = (
    "Stripe Checkout Session c таким session_id не обнаружена."
)
STRIPE_API_KEY_ERROR_MESSAGE = "Неверный Stripe API key."
SHOP_CART_CLEAR_MESSAGE = "Ваша корзина очищена, все товары из нее удалены."
COUPON_ERROR_MESSAGE = "Промокод {code} недействителен."


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="Retrieve a shopping cart",
        responses={200: ShoppingCartListSerializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Post and edit products in a shopping cart",
        responses={
            201: ShoppingCartListSerializer,
            400: ValidationErrorResponseSerializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Remove product from shopping cart",
        responses={200: ShoppingCartListSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="remove_all",
    decorator=swagger_auto_schema(
        operation_summary="Clear shopping cart",
        responses={
            200: ShoppingCartRemoveAllSerializer,
            400: ErrorResponse406Serializer,
        },
    ),
)
@method_decorator(
    name="coupon_apply",
    decorator=swagger_auto_schema(
        operation_summary="Apply promocode",
        responses={
            201: CouponSerializer,
            400: ErrorResponse406Serializer,
            403: ErrorResponse403Serializer,
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

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ShoppingCartListSerializer
        if self.action == "coupon_apply":
            return CouponSerializer
        return ShoppingCartSerializer

    # TODO: test this endpoint
    @transaction.atomic
    @action(detail=False, methods=["delete"], permission_classes=[permissions.AllowAny])
    def remove_all(self, request):
        """
        Deletes all the products from a user's shopping cart
        (both anonymous and authorized).
        """
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            logger.error(SHOP_CART_ERROR)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode406Enum.NOT_ACCEPTABLE,
                        "detail": SHOP_CART_ERROR,
                    }
                ],
            }
            return Response(
                ErrorResponse406Serializer(payload).data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.session.get("coupon_id"):
            del request.session["coupon_id"]
        shopping_cart.clear()
        logger.info(SHOP_CART_CLEAR_MESSAGE)
        payload = {"message": SHOP_CART_CLEAR_MESSAGE}
        return Response(
            ShoppingCartRemoveAllSerializer(payload).data, status=status.HTTP_200_OK
        )

    # TODO: test this endpoint
    @action(methods=["post"], detail=False)
    def coupon_apply(self, request):
        """Validates the promocode and saves it to the Django session."""
        shopping_cart = ShopCart(request)
        now = timezone.now()
        if not shopping_cart:
            logger.error(SHOP_CART_ERROR)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode406Enum.NOT_ACCEPTABLE,
                        "detail": SHOP_CART_ERROR,
                    }
                ],
            }
            return Response(
                ErrorResponse406Serializer(payload).data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer_class()
        code = request.data["code"]
        try:
            coupon = Coupon.objects.get(
                Q(code__iexact=code),
                Q(is_active=True),
                Q(start_time__lte=now) | Q(start_time__isnull=True),
                Q(end_time__gte=now) | Q(end_time__isnull=True),
            )
            request.session["coupon_id"] = coupon.id
            logger.info("Coupon id was saved in session.")
            return Response(
                serializer(
                    coupon,
                    context={
                        "request": request,
                        "format": self.format_kwarg,
                        "view": self,
                    },
                ).data,
                status=status.HTTP_201_CREATED,
            )
        except Coupon.DoesNotExist:
            request.session["coupon_id"] = None
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode403Enum.PERMISSION_DENIED,
                        "detail": COUPON_ERROR_MESSAGE.format(code=code),
                    }
                ],
            }
            return Response(
                ErrorResponse403Serializer(payload).data,
                status=status.HTTP_403_FORBIDDEN,
            )

    def list(self, request, **kwargs):
        """Returns a shopping cart of a user via Django session."""
        shopping_cart = ShopCart(request)
        serializer = self.get_serializer_class()
        coupon = shopping_cart.get_coupon()
        payload = {
            "products": shopping_cart.__iter__(),
            "count_of_products": shopping_cart.__len__(),
            "total_price": shopping_cart.get_total_price(),
            "coupon_code": coupon,
            "discount_amount": shopping_cart.get_coupon_shopping_cart_discount(coupon),
        }
        logger.info("The user's shopping cart list was successfully received.")
        return Response(serializer(payload).data, status=status.HTTP_200_OK)

    def create(self, request, **kwargs):
        """
        Adds new products to the shopping cart or edits the number of products
        already in the shopping cart (zero is not allowed).
        """
        if request.session.get("coupon_id"):
            del request.session["coupon_id"]
        shopping_cart = ShopCart(request)
        products = request.data["products"]
        serializer = ShoppingCartSerializer(data={"products": products})
        serializer.is_valid(raise_exception=True)
        for product in products:
            shopping_cart.add(product=product, quantity=product["quantity"])
        coupon = shopping_cart.get_coupon()
        payload = {
            "products": shopping_cart.__iter__(),
            "count_of_products": shopping_cart.__len__(),
            "total_price": shopping_cart.get_total_price(),
            "coupon_code": coupon,
            "discount_amount": shopping_cart.get_coupon_shopping_cart_discount(coupon),
        }
        logger.info("The shopping cart was successfully created.")
        return Response(
            ShoppingCartListSerializer(payload).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, **kwargs):
        """Removes a product from the shopping cart using its id."""
        if request.session.get("coupon_id"):
            del request.session["coupon_id"]
        shopping_cart = ShopCart(self.request)
        if not shopping_cart:
            logger.error(NO_SHOP_CART_ERROR_MESSAGE)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode404Enum.NOT_FOUND,
                        "detail": NO_SHOP_CART_ERROR_MESSAGE,
                    }
                ],
            }
            return Response(
                ErrorResponse404Serializer(payload).data,
                status=status.HTTP_404_NOT_FOUND,
            )
        product_id = int(self.kwargs["pk"])
        products = [product["id"] for product in shopping_cart.get_shop_products()]
        if product_id not in products:
            logger.error(SHOP_CART_ERROR_MESSAGE)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode404Enum.NOT_FOUND,
                        "detail": SHOP_CART_ERROR_MESSAGE,
                    }
                ],
            }
            return Response(
                ErrorResponse404Serializer(payload).data,
                status=status.HTTP_404_NOT_FOUND,
            )
        shopping_cart.remove(product_id)
        coupon = shopping_cart.get_coupon()
        payload = {
            "products": shopping_cart.__iter__(),
            "count_of_products": shopping_cart.__len__(),
            "total_price": shopping_cart.get_total_price(),
            "coupon_code": coupon,
            "discount_amount": shopping_cart.get_coupon_shopping_cart_discount(coupon),
        }
        logger.info(MESSAGE_ON_DELETE)
        return Response(
            ShoppingCartListSerializer(payload).data,
            status=status.HTTP_200_OK,
        )


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all orders",
        responses={200: OrderGetAuthSerializer, 401: ErrorResponse401Serializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get order by id",
        responses={
            200: OrderGetAuthSerializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create order",
        responses={
            201: OrderGetAnonSerializer,
            400: ValidationErrorResponseSerializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete order",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="pay",
    decorator=swagger_auto_schema(
        operation_summary="Online payment",
        responses={
            201: StripeSessionCreateSerializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
            500: ErrorResponse500Serializer,
        },
    ),
)
@method_decorator(
    name="successful_pay",
    decorator=swagger_auto_schema(
        operation_summary="Get order number after stripe payment",
        responses={
            200: StripePaySuccessPageSerializer,
            500: ErrorResponse500Serializer,
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
        if self.action == "successful_pay":
            return StripePaySuccessPageSerializer
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
        """
        Retrieves an order of a user by its id,
        anonymous users can only view anonymous orders,
        and authorized users can only view their own orders.
        """
        user = self.request.user
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if (user.is_anonymous and order.user is not None) or (
            user.is_authenticated and order.user != user
        ):
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode403Enum.PERMISSION_DENIED,
                        "detail": ORDER_USER_ERROR_MESSAGE,
                    }
                ],
            }
            return Response(
                ErrorResponse403Serializer(payload).data,
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(order)
        logger.info("The user's order was successfully received.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, **kwargs):
        """Returns a list of all the orders of an authorized user."""
        if self.request.user.is_authenticated:
            queryset = self.get_queryset().filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            logger.info("The user's order list was successfully received.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(METHOD_ERROR_MESSAGE)
        payload = {
            "type": ClientErrorEnum.CLIENT_ERROR,
            "errors": [
                {
                    "code": ErrorCode401Enum.NOT_AUTHENTICATED,
                    "detail": METHOD_ERROR_MESSAGE,
                }
            ],
        }
        return Response(
            ErrorResponse401Serializer(payload).data,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def create(self, request, *args, **kwargs):
        """Creates an order of a user (both anonymous and authorized)."""
        shopping_cart = ShopCart(request)
        if not shopping_cart:
            logger.error(SHOP_CART_ERROR)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode404Enum.NOT_FOUND,
                        "detail": SHOP_CART_ERROR,
                    }
                ],
            }
            return Response(
                ErrorResponse404Serializer(payload).data,
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
        order.order_number = generate_order_number()
        if shopping_cart.coupon_id:
            coupon = Coupon.objects.get(id=shopping_cart.coupon_id)
            order.coupon_applied = coupon
            order.coupon_discount = coupon.discount
        order.save()
        if request.session.get("coupon_id"):
            del request.session["coupon_id"]
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
        """Deletes an order by its id (authorized only)."""
        order_restricted_deletion_statuses = [
            Order.COLLECTING,
            Order.GATHERED,
            Order.DELIVERING,
            Order.DELIVERED,
            Order.COMPLETED,
        ]

        if self.request.user.is_anonymous:
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode401Enum.NOT_AUTHENTICATED,
                        "detail": DELETE_ORDER_BY_ANONYMOUS_ERROR_MESSAGE,
                    }
                ],
            }
            return Response(
                ErrorResponse401Serializer(payload).data,
                status=status.HTTP_401_UNAUTHORIZED,
            )
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user != self.request.user:
            logger.error(ORDER_USER_ERROR_MESSAGE)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode403Enum.PERMISSION_DENIED,
                        "detail": ORDER_USER_ERROR_MESSAGE,
                    }
                ],
            }
            return Response(
                ErrorResponse403Serializer(payload).data,
                status=status.HTTP_403_FORBIDDEN,
            )
        if order.status in order_restricted_deletion_statuses:
            logger.error(DELETE_ORDER_WITH_RESTRICTED_STATUS_ERROR_MESSAGE)
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode403Enum.PERMISSION_DENIED,
                        "detail": DELETE_ORDER_WITH_RESTRICTED_STATUS_ERROR_MESSAGE,
                    }
                ],
            }
            return Response(
                ErrorResponse403Serializer(payload).data,
                status=status.HTTP_403_FORBIDDEN,
            )
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
    @action(methods=["POST"], detail=True, permission_classes=[permissions.AllowAny])
    def pay(self, request, *args, **kwargs):
        """Creates a link for online payment for an order using Stripe."""
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user is not None and order.user != self.request.user:
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode403Enum.PERMISSION_DENIED,
                        "detail": PAY_SOMEONE_ELSE_ORDER_ERROR_MESSAGE.format(
                            pk=order.pk, user=request.user
                        ),
                    }
                ],
            }
            return Response(
                ErrorResponse403Serializer(payload).data,
                status=status.HTTP_403_FORBIDDEN,
            )
        if order.is_paid is True:
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode403Enum.PERMISSION_DENIED,
                        "detail": PAY_ALREADY_PAID_ORDER_ERROR_MESSAGE.format(
                            pk=order.pk
                        ),
                    }
                ],
            }
            return Response(
                ErrorResponse403Serializer(payload).data,
                status=status.HTTP_403_FORBIDDEN,
            )
        stripe.api_key = settings.STRIPE_SECRET_KEY
        current_site = get_current_site(request)
        if settings.MODE == "dev" or current_site.domain == "localhost":
            domain_url = f"http://{current_site}/"
        else:
            domain_url = f"https://{current_site}/"
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
                success_url=domain_url
                + "payment-is-processing?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url
                + "payment-cancelled?session_id={CHECKOUT_SESSION_ID}",
                client_reference_id=request.user.username
                if request.user.is_authenticated
                else None,
                payment_method_types=["card"],
                mode="payment",
                metadata={"order_id": order.id, "order_number": order.order_number},
            )
            logger.info("Stripe Checkout Session created successfully.")
            payload = {"checkout_session_url": checkout_session.url}
            return Response(
                StripeSessionCreateSerializer(payload).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            payload = {
                "type": ServerErrorEnum.SERVER_ERROR,
                "errors": [
                    {
                        "code": ErrorCode500Enum.ERROR,
                        "detail": STRIPE_SESSION_CREATE_ERROR_MESSAGE,
                        "attr": str(e),
                    }
                ],
            }
            return Response(
                ErrorResponse500Serializer(payload).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # TODO: test this endpoint
    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def successful_pay(self, request, *args, **kwargs):
        """Shows the order id and number from Stripe Checkout Session after payment."""
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_session_id = request.data["stripe_session_id"]
            session = stripe.checkout.Session.retrieve(stripe_session_id)
            payload = {
                "stripe_session_id": stripe_session_id,
                "order_id": session["metadata"]["order_id"],
                "order_number": session["metadata"]["order_number"],
            }
            return Response(
                StripePaySuccessPageSerializer(payload).data, status=status.HTTP_200_OK
            )
        except stripe._error.AuthenticationError as e:
            logger.error(f"{e}")
            payload = {
                "type": ServerErrorEnum.SERVER_ERROR,
                "errors": [
                    {
                        "code": ErrorCode500Enum.ERROR,
                        "detail": STRIPE_API_KEY_ERROR_MESSAGE,
                        "attr": str(e),
                    }
                ],
            }
            return Response(
                ErrorResponse500Serializer(payload).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except stripe._error.InvalidRequestError as e:
            logger.error(f"{e}")
            payload = {
                "type": ServerErrorEnum.SERVER_ERROR,
                "errors": [
                    {
                        "code": ErrorCode500Enum.ERROR,
                        "detail": STRIPE_INVALID_SESSION_ID_ERROR_MESSAGE,
                        "attr": str(e),
                    }
                ],
            }
            return Response(
                ErrorResponse500Serializer(payload).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
