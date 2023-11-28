from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import Order, OrderProduct
from products.models import Product
from users.models import User


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
        quantity_error_message = ("Укажите количество товара.")
        product_error_message = ("У нас нет таких продуктов. "
                                 "Выберете из представленных.")
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
        return obj.final_price

    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.name

    @extend_schema_field(str)
    def get_measure_unit(self, obj):
        return obj.measure_unit

    @extend_schema_field(int)
    def get_amount(self, obj):
        return obj.amount


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
            "address_anonymous",
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

    user = UserPresentSerializer(read_only=True)
    address = serializers.ReadOnlyField(source='user.address')

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
        )

    def validate_user(self, user):
        error_message = ("Добавьте номер телефона.")
        if not user.phone_number:
            raise serializers.ValidationError(error_message)
        return user

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        no_match_error_message = (
            "Способ получения заказа не соответствует способу оплаты."
        )
        error_message = ("Укажите адрес доставки!")
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

    # def to_representation(self, instance):
    #     return OrderGetAuthSerializer(instance, context=self.context).data


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
            "address_anonymous",
        )

    def validate_user_data(self, obj):
        """Checks user_data in order."""
        error_first_name = ("Необходимо указать контактные данные, "
                            "укажите имя!")
        error_last_name = ("Необходимо указать контактные данные, "
                           "укажите фамилию!")
        error_phone_number = ("Необходимо указать контактные данные, "
                              "укажите номер телефона!")
        error_email = ("Необходимо указать контактные данные, "
                       "укажите email!")
        user_data = obj.split(",")
        for data in user_data:
            data = data.split(":")
            if "first_name" not in data[0] and not data[1]:
                raise serializers.ValidationError(error_first_name)
            if "last_name" not in data[0] and not data[1]:
                raise serializers.ValidationError(error_last_name)
            if "phone_number" not in data[0] and not data[1]:
                raise serializers.ValidationError(error_phone_number)
            if "email" not in data[0] and not data[1]:
                raise serializers.ValidationError(error_email)
        return obj

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        no_match_error_message = (
            "Способ получения заказа не соответствует способу оплаты."
        )
        error_message = ("При выборе способа доставки курьером, "
                         "необходимо указать адрес доставки!")
        if not attrs["address_anonymous"] and attrs["delivery_method"] == Order.COURIER:
            raise serializers.ValidationError(error_message)
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

    # def to_representation(self, instance):
    #     return OrderGetAnonSerializer(instance, context=self.context).data
