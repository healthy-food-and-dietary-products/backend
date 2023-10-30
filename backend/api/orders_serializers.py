from django.db import transaction
from rest_framework import serializers

from .users_serializers import UserSerializer
from orders.models import Order, ShoppingCart, ShoppingCartProduct
from products.models import FavoriteProduct, Product


class ShoppingCartProductListSerializer(serializers.ModelSerializer):
    """Serializer products in shopping_cart."""

    id = serializers.ReadOnlyField(source="product.id")
    name = serializers.ReadOnlyField(source="product.name")
    measurement_unit = serializers.ReadOnlyField(source="product.measurement_unit")
    amount = serializers.ReadOnlyField(source="product.amount")
    price = serializers.ReadOnlyField(source="product.price")
    photo = serializers.ImageField(source="product.photo")
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCartProduct
        fields = (
            "id",
            "name",
            "photo",
            "measurement_unit",
            "price",
            "amount",
            "quantity",
            "is_favorited",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        product = obj.product
        if user.is_anonymous:
            return False
        # return product.is_favorited(user)
        return FavoriteProduct.objects.filter(user=user, product=product).exists()


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

    user = UserSerializer(read_only=True)
    products = ShoppingCartProductListSerializer(
        many=True, read_only=True, source="shopping_carts"
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ("id", "user", "products", "total_price", "status")

    def get_total_price(self, obj):  # TODO: add quantity:
        products = obj.products.all()
        total = 0
        for product in products:
            total += product.price
        return total


class ShoppingCartPostUpdateDeleteSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete shopping_cart."""

    user = UserSerializer(read_only=True)
    products = ShoppingCartProductCreateUpdateSerializer(many=True)

    class Meta:
        fields = "__all__"
        model = ShoppingCart

    def validate_products(self, data):
        products = []
        for i, val in enumerate(data):
            if not Product.objects.filter(id=val["id"]).exists():
                raise serializers.ValidationError(
                    "У нас нет таких продуктов! Выберете из представленных!"
                )
            products.append(val["id"])
        if len(products) != len(set(products)):
            raise serializers.ValidationError("Продукты не должны повторяться!")
        return data

    @transaction.atomic
    def create(self, validated_data):
        products = validated_data.pop("products")
        shop_cart = ShoppingCart.objects.filter(
            user=self.context["request"].user,
            status="In work",
        )
        if shop_cart:
            raise serializers.ValidationError(
                "Ваша корзина еще не оформлена, можно добавить продукты или изменить!"
            )
        shopping_cart = ShoppingCart.objects.create(
            **validated_data, user=self.context["request"].user
        )
        ShoppingCartProduct.objects.bulk_create(
            [
                ShoppingCartProduct(
                    shopping_cart=shopping_cart,
                    quantity=product["quantity"],
                    product=Product.objects.get(id=product["id"]),
                )
                for product in products
            ]
        )
        return shopping_cart

    @transaction.atomic
    def update(self, instance, validated_data):
        products = validated_data.pop("products", None)
        if products is not None:
            instance.products.clear()
        ShoppingCartProduct.objects.bulk_create(
            [
                ShoppingCartProduct(
                    shopping_cart=instance,
                    quantity=product["quantity"],
                    product=Product.objects.get(id=product["id"]),
                )
                for product in products
            ]
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShoppingCartGetSerializer(instance, context=self.context).data


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order representation."""

    user = serializers.ReadOnlyField(source="shopping_cart.user.username")

    class Meta:
        fields = (
            "id",
            "user",
            "order_number",
            "ordering_date",
            "status",
            "is_paid",
            "delivery_method",
        )
        model = Order
