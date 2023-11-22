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
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderProduct
        fields = ("id", "quantity")

    def validate_quantity(self, data):
        if data < 1:
            raise serializers.ValidationError("Укажите количество товара.")
        return data

    def validate_id(self, data):
        if not Product.objects.filter(id=data).exists():
            raise serializers.ValidationError(
                "У нас нет таких продуктов. Выберете из представленных."
            )
        return data


#     @transaction.atomic
#     def create(self, validated_data):
#         product = validated_data.pop("product")
#         quantity = validated_data.pop("quantity")
#         shopping_cart = validated_data.pop("shopping_cart")
#
#         return ShoppingCartProduct.objects.create(
#             product=product, quantity=quantity, shopping_cart=shopping_cart
#         )
#
#     @transaction.atomic
#     def update(self, instance, validated_data):
#         product = validated_data.pop("product")
#         quantity = validated_data.pop("quantity")
#         shopping_cart = validated_data.pop("shopping_cart")
#         shopping_cart_product = ShoppingCartProduct.objects.get(
#             product=product, quantity=quantity, shopping_cart=shopping_cart
#         )
#         if validated_data:
#             shopping_cart_product.save()

#
# class ShoppingCartGetSerializer(serializers.ModelSerializer):
#     """Serializer for shopping_cart representation."""
#
#     products = OrderProductListSerializer(
#         many=True, read_only=True, source="shopping_carts"
#     )
#
#     class Meta:
#         model = ShoppingCart
#         fields = ("id", "user", "products", "total_price")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete shopping_cart."""

    products = OrderProductSerializer(many=True)

    class Meta:
        fields = ("products",)
        model = Product

    def validate_products(self, data):
        products_id = [product["id"] for product in data]
        if len(products_id) != len(set(products_id)):
            raise serializers.ValidationError(
                "Продукты в корзине не должны повторяться."
            )
        return data


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
        return obj.shopping_cart.total_price + obj.package

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

    products = OrderProductSerializer(many=True)

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

    def validate_address(self, address):
        """Checks that the user has not entered someone else's address."""
        if address.user != self.context["request"].user:
            raise serializers.ValidationError(
                "Данный адрес доставки принадлежит другому пользователю."
            )
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

    # @transaction.atomic
    # def create(self, validated_data):
    #     user = self.context["request"].user
    #     try:
    #         shopping_cart = ShoppingCart.objects.get(
    #             user=user, status=ShoppingCart.INWORK
    #         )
    #     except Exception:
    #         raise serializers.ValidationError(
    #             "У вас нет продуктов для заказа, наполните корзину."
    #         )
    #     payment_method = validated_data.pop("payment_method")
    #     delivery_method = validated_data.pop("delivery_method")
    #     package = validated_data.pop("package")
    #     comment = validated_data.pop("comment")
    #     if delivery_method == Order.DELIVERY_POINT:
    #         if not validated_data.get("delivery_point"):
    #             raise serializers.ValidationError("Нужно выбрать пункт выдачи.")
    #         delivery_point = Delivery.objects.get(
    #             delivery_point=validated_data.pop("delivery_point")
    #         )
    #         address = None
    #     else:
    #         if not validated_data.get("address"):
    #             raise serializers.ValidationError("Нужно указать адрес доставки.")
    #         address = Address.objects.get(address=validated_data.pop("address"))
    #         delivery_point = None
    # shopping_cart.status = ShoppingCart.ORDERED
    # shopping_cart.save()
    # for product in shopping_cart.products.all():
    #     product.orders_number += 1
    #     product.save()
    #     return Order.objects.create(
    #         user=user,
    #         shopping_cart=shopping_cart,
    #         status=Order.ORDERED,
    #         payment_method=payment_method,
    #         delivery_method=delivery_method,
    #         delivery_point=delivery_point,
    #         package=package,
    #         comment=comment,
    #         address=address,
    #     )
    #
    # def to_representation(self, instance):
    #     return OrderListSerializer(instance, context=self.context).data
