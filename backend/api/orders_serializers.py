from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import Order, OrderProduct
from products.models import Product
from users.models import User


class UserPresentSerializer(UserSerializer):
    class Meta:
        fields = ("username", "first_name", "last_name")
        model = User


class OrderProductListSerializer(serializers.ModelSerializer):
    """Serializer products in shopping_cart."""

    id = serializers.ReadOnlyField(source="product.id")
    name = serializers.ReadOnlyField(source="product.name")
    measure_unit = serializers.ReadOnlyField(source="product.measure_unit")
    amount = serializers.ReadOnlyField(source="product.amount")
    price = serializers.ReadOnlyField(source="product.price")
    final_price = serializers.SerializerMethodField()
    is_favorited_by_user = serializers.SerializerMethodField()

    class Meta:
        model = OrderProduct
        fields = (
            "id",
            "name",
            "measure_unit",
            "price",
            "final_price",
            "amount",
            "quantity",
            "is_favorited_by_user",
        )

    @extend_schema_field(bool)
    def get_is_favorited_by_user(self, obj):
        """Checks if this product is in the buyer's favorites."""

        return bool(obj.shopping_cart.user.favorites.filter(product=obj.product))

    @extend_schema_field(float)
    def get_final_price(self, obj):
        return obj.product.final_price


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


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete shopping_cart."""

    products = OrderProductSerializer(many=True)

    class Meta:
        fields = ("products",)
        model = OrderProduct


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order representation."""

    # products = OrderProductListSerializer(many=True)
    user = UserPresentSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    address = serializers.StringRelatedField()
    delivery_point = serializers.StringRelatedField()
    # order_number = serializers.SerializerMethodField()

    @extend_schema_field(int)
    def get_order_number(self, obj):
        return obj.id

    @extend_schema_field(float)
    def get_total_price(self, obj):
        return obj.total_price

    class Meta:
        fields = (
            "id",
            "user",
            "products",
            "order_number",
            "ordering_date",
            "status",
            "payment_method",
            "is_paid",
            "delivery_method",
            "address",
            "delivery_point",
            "package",
            "comment",
            "total_price",
        )
        model = Order

    # def get_queryset(self):
    #     return Order.objects.filter(user=self.get_user())


class OrderPostDeleteSerializer(serializers.ModelSerializer):
    """Serializer for create/delete authorized order."""

    class Meta:
        model = Order
        fields = (
            "user",
            "order_number",
            "products",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            "comment",
            "address",
        )

    def validate_address(self, address):
        """Checks that the user has not entered someone else's address."""
        error_message = (
            "Данный адрес доставки принадлежит другому пользователю.")
        if address.user != self.context["request"].user:
            raise serializers.ValidationError(error_message)
        return address

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        no_match_error_message = (
            "Способ получения заказа не соответствует способу оплаты."
        )
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
    #     return OrderListSerializer(instance, context=self.context).data


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for create/delete anonim order."""

    class Meta:
        model = Order
        fields = (
            "order_number",
            "user_data",
            "products",
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

    def validate_address_anonymous(self, obj):
        """Checks that the user has address when order by courier."""
        error_message = ("При выборе способа доставки курьером, "
                         "необходимо указать адрес доставки!")
        if not obj.address and obj.delivery_method == Order.COURIER:
            raise serializers.ValidationError(error_message)
        return obj

    def validate(self, attrs):
        """Checks that the payment method matches the delivery method."""
        no_match_error_message = (
            "Способ получения заказа не соответствует способу оплаты."
        )
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
