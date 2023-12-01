import re

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import Order, OrderProduct
from products.models import Product
from users.models import PHONE_NUMBER_ERROR, PHONE_NUMBER_REGEX, Address, User

NO_MATCH_ERROR_MESSAGE = "Способ получения заказа не соответствует способу оплаты."
COURIER_DELIVERY_ERROR_MESSAGE = (
    "При выборе способа доставки курьером, "
    "необходимо указать адрес доставки!"
)
DELIVERY_ERROR_MESSAGE = "Укажите способ доставки."
PAYMENT_ERROR_MESSAGE = "Нужно выбрать способ оплаты."
DELIVERY_POINT_ERROR_MESSAGE = "Нужно выбрать пункт выдачи."
ADDRESS_ERROR_MESSAGE = "Добавьте адрес доставки."
QUANTITY_ERROR_MESSAGE = "Укажите количество товара."
PRODUCT_ERROR_MESSAGE = (
    "У нас нет таких продуктов. " "Выберете из представленных."
)

PHONE_NUMBER_ERROR_MESSAGE = (
    "Добавьте номер телефона в своем "
    "Личном кабинете/Профиле."
)


class UserPresentSerializer(UserSerializer):
    class Meta:
        fields = ("username", "first_name", "last_name", "phone_number")
        model = User


class OrderProductSerializer(serializers.ModelSerializer):
    """Serializer for add/update/delete products into shopping_cart."""

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


class OrderProductListSerializer(serializers.ModelSerializer):
    """Serializer products in order."""

    name = serializers.SerializerMethodField()
    measure_unit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = OrderProduct
        fields = (
            "id",
            "name",
            "measure_unit",
            "amount",
            "quantity",
            "final_price",
        )

    @extend_schema_field(float)
    def get_final_price(self, obj):
        if isinstance(obj, dict):
            product = Product.objects.get(id=obj["id"])
            return product.final_price
        if isinstance(obj, OrderProduct):
            return obj.product.final_price
        return obj.final_price

    @extend_schema_field(str)
    def get_name(self, obj):
        if isinstance(obj, dict):
            return obj["name"]
        if isinstance(obj, OrderProduct):
            return obj.product.name
        return obj.name

    @extend_schema_field(str)
    def get_measure_unit(self, obj):
        if isinstance(obj, dict):
            product = Product.objects.get(id=obj["id"])
            return product.measure_unit
        if isinstance(obj, OrderProduct):
            return obj.product.measure_unit
        return obj.measure_unit

    @extend_schema_field(int)
    def get_amount(self, obj):
        if isinstance(obj, dict):
            product = Product.objects.get(id=obj["id"])
            return product.amount
        if isinstance(obj, OrderProduct):
            return obj.product.amount
        return obj.amount

    @extend_schema_field(int)
    def get_quantity(self, obj):
        if isinstance(obj, dict):
            return obj["quantity"]
        return None


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete shopping_cart."""

    products = OrderProductSerializer(many=True)

    class Meta:
        fields = ("products",)
        model = OrderProduct


class OrderGetAuthSerializer(serializers.ModelSerializer):
    """Serializer for authorized user order representation."""

    products = OrderProductListSerializer(many=True)
    user = UserPresentSerializer(read_only=True)

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
        )
        model = Order


class OrderGetAnonSerializer(serializers.ModelSerializer):
    """Serializer for anonimous user order representation."""

    products = OrderProductListSerializer(many=True)

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
        )
        model = Order


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

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        user = self.context["request"].user
        if not user.phone_number:
            raise serializers.ValidationError(PHONE_NUMBER_ERROR_MESSAGE)
        address = Address.objects.filter(user=user)
        if not address and "add_address" not in attrs:
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

    def validate_add_addres(self, add_address):
        """Check add_address in user_data."""
        if add_address == "":
            raise serializers.ValidationError(ADDRESS_ERROR_MESSAGE)
        return add_address


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
