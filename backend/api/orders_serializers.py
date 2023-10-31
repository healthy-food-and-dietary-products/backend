from django.db import transaction
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import ShoppingCart, ShoppingCartProduct
from products.models import Product
from users.models import User


class UserPresentSerializer(UserSerializer):
    class Meta:
        fields = ("username", "first_name", "last_name")
        model = User


class ShoppingCartProductListSerializer(serializers.ModelSerializer):
    """Serializer products in shopping_cart."""

    id = serializers.ReadOnlyField(source="product.id")
    name = serializers.ReadOnlyField(source="product.name")
    measurement_unit = serializers.ReadOnlyField(source="product.measurement_unit")
    amount = serializers.ReadOnlyField(source="product.amount")
    price = serializers.ReadOnlyField(source="product.price")
    # is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCartProduct
        fields = (
            "id",
            "name",
            "measurement_unit",
            "price",
            "amount",
            "quantity",
            # "is_favorited",
        )

    # def get_is_favorited(self, obj):
    #     user = self.context["request"].user
    #
    #     return FavoriteProduct.objects.filter(user=user, product=obj).exists()


class ShoppingCartProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for add/update/delete products into shopping_cart."""

    id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = ShoppingCartProduct
        fields = ("id", "quantity")

    def validate_quantity(self, data):
        if data < 1:
            raise serializers.ValidationError("Укажите количество товара!")
        return data

    def validate_id(self, data):
        if not Product.objects.filter(id=data).exists():
            raise serializers.ValidationError(
                "У нас нет таких продуктов! Выберете из представленных!"
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
        fields = ("user", "products", "total_price", "status")
        model = ShoppingCart

    def to_representation(self, instance):
        return ShoppingCartGetSerializer(instance, context=self.context).data
