import json
import re

from django.db.models import Prefetch
from rest_framework import serializers

from .products_serializers import CouponLightSerializer, ProductPresentSerializer
from .users_serializers import UserSerializer
from orders.models import Order, OrderProduct
from products.models import Product
from users.models import PHONE_NUMBER_ERROR, PHONE_NUMBER_REGEX, User

NO_MATCH_ERROR_MESSAGE = "Способ получения заказа не соответствует способу оплаты."
COURIER_DELIVERY_ERROR_MESSAGE = (
    "При выборе способа доставки курьером необходимо указать адрес доставки."
)
DELIVERY_ERROR_MESSAGE = "Укажите способ доставки."
PAYMENT_ERROR_MESSAGE = "Нужно выбрать способ оплаты."
DELIVERY_POINT_ERROR_MESSAGE = "Нужно выбрать пункт выдачи."
ADDRESS_ERROR_MESSAGE = "Добавьте адрес доставки."
QUANTITY_ERROR_MESSAGE = "Укажите количество товара."
PRODUCT_ERROR_MESSAGE = "У нас нет таких продуктов, выберите из представленных."
PHONE_NUMBER_ERROR_MESSAGE = "Добавьте номер телефона в своем Личном кабинете/Профиле."


class UserPresentSerializer(UserSerializer):
    class Meta:
        fields = ("username", "first_name", "last_name", "phone_number")
        model = User


class ShoppingCartProductSerializer(serializers.ModelSerializer):
    """Serializer to add/edit products in shopping cart."""

    id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderProduct
        fields = ("id", "quantity")

    def validate(self, attrs):
        if attrs["quantity"] < 1 or None:
            raise serializers.ValidationError(QUANTITY_ERROR_MESSAGE)
        if not Product.objects.filter(id=attrs["id"]).exists():
            raise serializers.ValidationError(PRODUCT_ERROR_MESSAGE)
        return attrs


class OrderProductDisplaySerializer(serializers.ModelSerializer):
    """Serializer to display order products in order."""

    product = ProductPresentSerializer()

    class Meta:
        model = OrderProduct
        fields = ("product", "quantity")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer to create/edit shopping cart."""

    products = ShoppingCartProductSerializer(many=True)

    class Meta:
        fields = ("products",)
        model = Product


class ShoppingCartProductListSerializer(serializers.Serializer):
    """Serializer for the list of products in the shopping cart."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    photo = serializers.CharField(read_only=True)
    final_price = serializers.FloatField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.FloatField(read_only=True)
    category = serializers.SlugField(read_only=True)
    amount = serializers.IntegerField(read_only=True)
    measure_unit = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class ShoppingCartListSerializer(serializers.Serializer):
    """Serializer to display the shopping cart using the GET method."""

    products = ShoppingCartProductListSerializer(many=True, read_only=True)
    count_of_products = serializers.IntegerField(read_only=True)
    total_price = serializers.FloatField(read_only=True)


class OrderGetAuthSerializer(serializers.ModelSerializer):
    """Serializer for authorized user order representation."""

    products = OrderProductDisplaySerializer(source="orders", many=True)
    user = UserPresentSerializer(read_only=True)
    coupon = CouponLightSerializer(source="coupon_applied", read_only=True)

    class Meta:
        fields = (
            "id",
            "order_number",
            "user",
            "products",
            "payment_method",
            "delivery_method",
            "address",
            "add_address",
            "delivery_point",
            "package",
            "comment",
            "total_price",
            "is_paid",
            "status",
            "ordering_date",
            "coupon",
        )
        model = Order

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Perform necessary eager loading of orders data."""
        return queryset.select_related("user", "coupon_applied").prefetch_related(
            Prefetch(
                "orders",
                queryset=OrderProduct.objects.select_related(
                    "product__category",
                ).prefetch_related("product__promotions"),
            )
        )


class OrderGetAnonSerializer(serializers.ModelSerializer):
    """Serializer for anonimous user order representation."""

    products = OrderProductDisplaySerializer(source="orders", many=True)
    user_data = serializers.SerializerMethodField()
    coupon = CouponLightSerializer(source="coupon_applied", read_only=True)

    class Meta:
        fields = (
            "id",
            "order_number",
            "user_data",
            "products",
            "payment_method",
            "delivery_method",
            "add_address",
            "delivery_point",
            "package",
            "comment",
            "total_price",
            "is_paid",
            "status",
            "ordering_date",
            "coupon",
        )
        model = Order

    def get_user_data(self, obj):
        if obj.user_data is not None:
            return json.loads(str(obj.user_data).replace("'", '"'))
        return None


class OrderCreateAuthSerializer(serializers.ModelSerializer):
    """Serializer for create authorized order."""

    class Meta:
        model = Order
        fields = (
            "user",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            "comment",
            "address",
            "add_address",
        )

    def validate_add_address(self, add_address):
        """Check add_address field for authorized user."""
        if len(add_address) < 1:
            raise serializers.ValidationError(ADDRESS_ERROR_MESSAGE)
        return add_address

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        user = self.context["request"].user
        if not user.phone_number:
            raise serializers.ValidationError(PHONE_NUMBER_ERROR_MESSAGE)
        if (
            attrs["delivery_method"] == Order.COURIER
            and "address" not in attrs
            and "add_address" not in attrs
        ):
            raise serializers.ValidationError(ADDRESS_ERROR_MESSAGE)
        if "delivery_method" not in attrs:
            raise serializers.ValidationError(DELIVERY_ERROR_MESSAGE)
        if "payment_method" not in attrs:
            raise serializers.ValidationError(PAYMENT_ERROR_MESSAGE)
        if (
            attrs["delivery_method"] == Order.DELIVERY_POINT
            and "delivery_point" not in attrs
        ):
            raise serializers.ValidationError(DELIVERY_POINT_ERROR_MESSAGE)
        if (
            attrs["payment_method"] == Order.DELIVERY_POINT_PAYMENT
            and attrs["delivery_method"] == Order.COURIER
        ):
            raise serializers.ValidationError(NO_MATCH_ERROR_MESSAGE)
        if (
            attrs["payment_method"] == Order.COURIER_CASH_PAYMENT
            and attrs["delivery_method"] == Order.DELIVERY_POINT
        ):
            raise serializers.ValidationError(NO_MATCH_ERROR_MESSAGE)
        if attrs["delivery_method"] == Order.COURIER and Order.address is None:
            raise serializers.ValidationError(COURIER_DELIVERY_ERROR_MESSAGE)
        return super().validate(attrs)


class AnonUserDataSerializer(serializers.Serializer):
    """Serializer for anonymous user user_data"""

    first_name = serializers.CharField(max_length=256)
    last_name = serializers.CharField(max_length=256)
    phone_number = serializers.CharField(max_length=256)
    email = serializers.EmailField()

    def validate_phone_number(self, phone_number):
        """Checks phone_number in user_data."""
        if not re.match(PHONE_NUMBER_REGEX, phone_number):
            raise serializers.ValidationError(PHONE_NUMBER_ERROR)
        return phone_number


class OrderCreateAnonSerializer(serializers.ModelSerializer):
    """Serializer for create/delete anonim order."""

    user_data = AnonUserDataSerializer()

    class Meta:
        model = Order
        fields = (
            "user_data",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            "comment",
            "add_address",
        )

    def validate_add_address(self, add_address):
        """Check add_address field for anonymous user."""
        if len(add_address) < 1:
            raise serializers.ValidationError(ADDRESS_ERROR_MESSAGE)
        return add_address

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        if "delivery_method" not in attrs:
            raise serializers.ValidationError(DELIVERY_ERROR_MESSAGE)
        if "payment_method" not in attrs:
            raise serializers.ValidationError(PAYMENT_ERROR_MESSAGE)
        if attrs["delivery_method"] == Order.COURIER and "add_address" not in attrs:
            raise serializers.ValidationError(COURIER_DELIVERY_ERROR_MESSAGE)
        if (
            attrs["delivery_method"] == Order.DELIVERY_POINT
            and "delivery_point" not in attrs
        ):
            raise serializers.ValidationError(DELIVERY_POINT_ERROR_MESSAGE)
        if (
            attrs["payment_method"] == Order.DELIVERY_POINT_PAYMENT
            and attrs["delivery_method"] == Order.COURIER
        ):
            raise serializers.ValidationError(NO_MATCH_ERROR_MESSAGE)
        if (
            attrs["payment_method"] == Order.COURIER_CASH_PAYMENT
            and attrs["delivery_method"] == Order.DELIVERY_POINT
        ):
            raise serializers.ValidationError(NO_MATCH_ERROR_MESSAGE)
        return super().validate(attrs)


class StripeCheckoutSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer to create Stripe Checkout Session to pay an order."""

    class Meta:
        model = Order
        fields = tuple()


class StripeSessionCreateSerializer(serializers.Serializer):
    """Serializer to show Stripe Checkout Session URL."""

    checkout_session_url = serializers.URLField()


class StripePaySuccessPageSerializer(serializers.Serializer):
    """Serializer to get the order number from Stripe Checkout Session after payment."""

    stripe_session_id = serializers.CharField()
    order_id = serializers.CharField(read_only=True)
    order_number = serializers.CharField(read_only=True)


class StripeError500Serializer(serializers.Serializer):
    """Serializer for errors during Stripe payments."""

    message = serializers.CharField()
    errors = serializers.CharField()


class CustomSuccessSerializer(serializers.Serializer):
    """Serializer for custom success messages."""

    message = serializers.CharField()


class CustomErrorSerializer(serializers.Serializer):
    """Serializer for custom errors."""

    errors = serializers.CharField()
