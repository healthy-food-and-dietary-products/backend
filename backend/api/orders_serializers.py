from django.db import transaction
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import Delivery, Order, ShoppingCart, ShoppingCartProduct
from products.models import Product
from users.models import Address, User


class UserPresentSerializer(UserSerializer):
    class Meta:
        fields = ("username", "first_name", "last_name")
        model = User


class ShoppingCartProductListSerializer(serializers.ModelSerializer):
    """Serializer products in shopping_cart."""

    id = serializers.ReadOnlyField(source="product.id")
    name = serializers.ReadOnlyField(source="product.name")
    measure_unit = serializers.ReadOnlyField(source="product.measure_unit")
    amount = serializers.ReadOnlyField(source="product.amount")
    final_price = serializers.ReadOnlyField(source="product.final_price")
    is_favorited_by_user = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCartProduct
        fields = (
            "id",
            "name",
            "measure_unit",
            "final_price",
            "amount",
            "quantity",
            "is_favorited_by_user",
        )

    def get_is_favorited_by_user(self, obj):
        """Checks if this product is in the buyer's favorites."""
        return bool(obj.shopping_cart.user.favorites.filter(product=obj.product))


class ShoppingCartProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for add/update/delete products into shopping_cart."""

    id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = ShoppingCartProduct
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

    @transaction.atomic
    def create(self, validated_data):
        product = validated_data.pop("product")
        quantity = validated_data.pop("quantity")
        shopping_cart = validated_data.pop("shopping_cart")

        return ShoppingCartProduct.objects.create(
            product=product, quantity=quantity, shopping_cart=shopping_cart
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        product = validated_data.pop("product")
        quantity = validated_data.pop("quantity")
        shopping_cart = validated_data.pop("shopping_cart")
        shopping_cart_product = ShoppingCartProduct.objects.get(
            product=product, quantity=quantity, shopping_cart=shopping_cart
        )
        if validated_data:
            shopping_cart_product.save()


class ShoppingCartGetSerializer(serializers.ModelSerializer):
    """Serializer for shopping_cart representation."""

    user = UserPresentSerializer(read_only=True)
    products = ShoppingCartProductListSerializer(
        many=True, read_only=True, source="shopping_carts"
    )

    class Meta:
        model = ShoppingCart
        fields = ("id", "user", "products", "total_price", "status")


class ShoppingCartPostUpdateDeleteSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete shopping_cart."""

    products = ShoppingCartProductCreateUpdateSerializer(many=True)

    class Meta:
        fields = ("products",)
        model = ShoppingCart

    def to_representation(self, instance):
        return ShoppingCartGetSerializer(instance, context=self.context).data


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order representation."""

    user = UserPresentSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    shopping_cart = ShoppingCartGetSerializer(read_only=True)
    address = serializers.StringRelatedField()
    delivery_point = serializers.StringRelatedField()
    order_number = serializers.SerializerMethodField()

    def get_order_number(self, obj):
        return obj.shopping_cart.id

    def get_total_price(self, obj):
        return obj.shopping_cart.total_price + obj.package

    class Meta:
        fields = (
            "id",
            "user",
            "shopping_cart",
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
            "order_number",
            "payment_method",
            "delivery_method",
            "delivery_point",
            "package",
            # "total_price", # TODO: add method
            "comment",
            "address",
        )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        try:
            shopping_cart = ShoppingCart.objects.get(user=user, status="In work")
        except Exception:
            raise serializers.ValidationError(
                "У вас нет продуктов для заказа, наполните корзину."
            )
        payment_method = validated_data.pop("payment_method")
        delivery_method = validated_data.pop("delivery_method")
        package = validated_data.pop("package")
        comment = validated_data.pop("comment")
        if delivery_method == "Point of delivery":
            delivery_point = validated_data.pop("delivery_point")
            if not delivery_point:
                raise serializers.ValidationError("Нужно выбрать пункт выдачи.")
            delivery_point = Delivery.objects.get(delivery_point=delivery_point)
            address = None
        else:
            address = Address.objects.get(address=validated_data.pop("address"))
            if not address:
                raise serializers.ValidationError("Нужно указать адрес доставки.")
            delivery_point = None
        shopping_cart.status = "Ordered"
        shopping_cart.save()
        return Order.objects.create(
            user=user,
            shopping_cart=shopping_cart,
            status="Ordered",
            payment_method=payment_method,
            delivery_method=delivery_method,
            delivery_point=delivery_point,
            package=package,
            comment=comment,
            address=address,
        )

    def to_representation(self, instance):
        return OrderListSerializer(instance, context=self.context).data
