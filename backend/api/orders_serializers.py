import re

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import Order, OrderProduct
from products.models import Product
from users.models import Address, User

EMAIL_REGEX = r"\S+@\S+\.\S+"
PHONE_NUMBER_REGEX = r"^(\+7|7|8)\d{10}$"


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
        quantity_error_message = "Укажите количество товара."
        product_error_message = (
            "У нас нет таких продуктов. " "Выберете из представленных."
        )
        if attrs["quantity"] < 1 or None:
            raise serializers.ValidationError(quantity_error_message)

        if not Product.objects.filter(id=attrs["id"]).exists():
            raise serializers.ValidationError(product_error_message)

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
            "order_number",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            "comment",
            "address",
            "add_address"
        )

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        no_match_error_message = (
            "Способ получения заказа не соответствует способу оплаты."
        )
        error_message = "Укажите адрес доставки."
        error_delivery_message = ("Укажите способ доставки.")
        error_delivery_point_message = ("Нужно выбрать пункт выдачи.")
        error_payment_message = ("Нужно выбрать способ оплаты.")
        error_address_message = ("Добавьте адрес доставки.")
        error_phone_number_message = ("Добавьте номер телефона.")
        user = self.context["request"].user
        if not user.phone_number:
            raise serializers.ValidationError(error_phone_number_message)
        address = Address.objects.filter(user=user)
        if not address and "add_address" not in attrs:
            raise serializers.ValidationError(error_address_message)
        if "delivery_method" not in attrs:
            raise serializers.ValidationError(error_delivery_message)
        if "payment_method" not in attrs:
            raise serializers.ValidationError(error_payment_message)
        if (attrs["delivery_method"] == Order.DELIVERY_POINT
                and "delivery_point" not in attrs):
            raise serializers.ValidationError(error_delivery_point_message)
        if (
            attrs["payment_method"] == Order.DELIVERY_POINT_PAYMENT
            and attrs["delivery_method"] == Order.COURIER
        ):
            raise serializers.ValidationError(no_match_error_message)
        if (
            attrs["payment_method"] == Order.COURIER_CASH_PAYMENT
            and attrs["delivery_method"] == Order.DELIVERY_POINT
        ):
            raise serializers.ValidationError(no_match_error_message)
        if attrs["delivery_method"] == Order.COURIER and Order.address is None:
            raise serializers.ValidationError(error_message)

        return super().validate(attrs)

    def to_representation(self, instance):
        return OrderGetAuthSerializer(instance, context=self.context).data


class OrderCreateAnonSerializer(serializers.ModelSerializer):
    """Serializer for create/delete anonim order."""

    class Meta:
        model = Order
        fields = (
            "order_number",
            "user_data",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            "comment",
            "add_address",
        )

    def validate_user_data(self, user_data):
        """Checks user_data in order."""
        error_first_name = "Необходимо указать контактные данные, " "укажите имя!"
        error_last_name = "Необходимо указать контактные данные, " "укажите фамилию!"
        error_phone_number = ("Необходимо указать контактные данные, "
                              "укажите номер телефона!")
        error_email = "Необходимо указать контактные данные, " "укажите email!"
        validate_phone_error_message = (
            "Введен некорректный номер телефона. "
            "Введите номер телефона в форматах "
            "'+7XXXXXXXXXX', '7XXXXXXXXXX' или '8XXXXXXXXXX'."
        )
        validate_email_error_message = ("Проверьте корректность написания "
                                        "электронной почты.")

        u_data = user_data.split(",")
        for data in u_data:
            data = data.strip().split(":")
            if data[0] == "first_name" and not data[1]:
                raise serializers.ValidationError(error_first_name)
            if data[0] == "last_name" and not data[1]:
                raise serializers.ValidationError(error_last_name)
            if data[0] == "phone_number":
                if not data[1]:
                    raise serializers.ValidationError(error_phone_number)
                if not re.match(PHONE_NUMBER_REGEX, data[1].strip()):
                    raise serializers.ValidationError(validate_phone_error_message)
            if data[0] == "email":
                if not data[1]:
                    raise serializers.ValidationError(error_email)
                if not re.match(EMAIL_REGEX, data[1].strip()):
                    raise serializers.ValidationError(validate_email_error_message)
        return user_data

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        no_match_error_message = (
            "Способ получения заказа не соответствует способу оплаты."
        )
        error_message = (
            "При выборе способа доставки курьером, "
            "необходимо указать адрес доставки!"
        )
        error_delivery_message = ("Укажите способ доставки.")
        error_payment_message = ("Нужно выбрать способ оплаты.")
        error_delivery_point_message = ("Нужно выбрать пункт выдачи.")
        if "delivery_method" not in attrs:
            raise serializers.ValidationError(error_delivery_message)
        if "payment_method" not in attrs:
            raise serializers.ValidationError(error_payment_message)
        if (attrs["delivery_method"] == Order.COURIER
                and "add_address" not in attrs):
            raise serializers.ValidationError(error_message)
        if (attrs["delivery_method"] == Order.DELIVERY_POINT
                and "delivery_point" not in attrs):
            raise serializers.ValidationError(error_delivery_point_message)
        if (
            attrs["payment_method"] == Order.DELIVERY_POINT_PAYMENT
            and attrs["delivery_method"] == Order.COURIER
        ):
            raise serializers.ValidationError(no_match_error_message)
        if (
            attrs["payment_method"] == Order.COURIER_CASH_PAYMENT
            and attrs["delivery_method"] == Order.DELIVERY_POINT
        ):
            raise serializers.ValidationError(no_match_error_message)

        return super().validate(attrs)

    def to_representation(self, instance):
        return OrderGetAnonSerializer(instance, context=self.context).data
