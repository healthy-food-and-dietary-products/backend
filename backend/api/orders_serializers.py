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
        if attrs["quantity"] < 1 or None:
            raise serializers.ValidationError("Укажите количество товара.")

        if not Product.objects.filter(id=attrs["id"]).exists():
            raise serializers.ValidationError(
                "У нас нет таких продуктов. Выберете из представленных."
            )
        return attrs


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete shopping_cart."""

    products = OrderProductSerializer(many=True)

    class Meta:
        fields = ("products",)
        model = OrderProduct


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order representation."""

    products = OrderProductSerializer(many=True)
    user = UserPresentSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    address = serializers.StringRelatedField()
    delivery_point = serializers.StringRelatedField()
    order_number = serializers.SerializerMethodField()

    @extend_schema_field(int)
    def get_order_number(self, obj):
        return obj.shopping_cart.id

    @extend_schema_field(float)
    def get_total_price(self, obj):
        return (
            round(
                sum(
                    [
                        (float(Product.objects.get(id=product["id"]).final_price))
                        * int(product["quantity"])
                        for product in obj.products
                    ]
                ),
                2,
            )
            + obj.package
        )

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

    def get_queryset(self):
        return Order.objects.filter(user=self.get_user())


class OrderPostDeleteSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete order."""

    class Meta:
        model = Order
        fields = (
            "products",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            "comment",
            "address",
        )

    # TODO: allow to create new address during order creation
    # TODO: if user chooses existing address, check that it is his/her address

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
