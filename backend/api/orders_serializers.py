from django.db import transaction
from rest_framework import serializers

from orders.models import Order, ShoppingCart, ShoppingCartProduct
from products.models import Product, FavoriteProduct
from users.models import User
from .users_serializers import UserSerializer


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
            "is_favorited"
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        product = obj.product
        if user.is_anonymous:
            return False
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
            raise serializers.ValidationError(
                "Укажите количество товара!"
            )
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        product = validated_data.pop("product")
        quantity = validated_data.pop("quantity")
        shopping_cart = validated_data.pop("shopping_cart")
        shopping_cart_product = ShoppingCartProduct.objects.create(
            product=product, quantity=quantity, shopping_cart=shopping_cart
        )
        return shopping_cart_product

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

    products = ShoppingCartProductListSerializer(
        many=True, read_only=True, source="shopping_carts"
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ("id", "user", "products", "total_price")

    def get_total_price(self, obj):
        print(obj, ">>>>>>>>>>>>>>>>")
        total = 0
        # for product in obj.products.all():
        #     print(product)
        #     total += product.price * product.quantity
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
            if not Product.objects.filter(id=val['id']).exists():
                raise serializers.ValidationError(
                    'Нужно выбрать продукт из представленных!')
            products.append(val['id'])
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                'Продукты не должны повторяться!')
        return data
    
    # @transaction.atomic
    # def create(self, validated_data):
    #     products = validated_data.pop("products")
    #     shop_cart = ShoppingCart.objects.filter(
    #         user=self.context["request"].user,
    #         status="В работе",
    #     )
    #     if shop_cart:
    #         raise serializers.ValidationError(
    #             'Ваша корзина еще не оформлена, можно добавить продукты или изменить!')
    #     shopping_cart = ShoppingCart.objects.create(
    #         **validated_data, user=self.context["request"].user
    #     )
    #     ShoppingCartProduct.objects.bulk_create(
    #         [
    #             ShoppingCartProduct(
    #                 shopping_cart=shopping_cart,
    #                 quantity=product["quantity"],
    #                 product=Product.objects.get(id=product["id"]),
    #             )
    #             for product in products
    #         ]
    #     )
    #     return shopping_cart
    #
    # @transaction.atomic
    # def update(self, instance, validated_data):
    #     products = validated_data.pop("products", None)
    #     if products is not None:
    #         instance.products.append(products)
    #
    #     ShoppingCartProducts.objects.bulk_create(
    #         [
    #             ShoppingCartProduct(
    #                 shopping_cart=shopping_cart,
    #                 quantity=product["quantity"],
    #                 product=Product.objects.get(id=product["id"]),
    #             )
    #             for product in products
    #         ]
    #     )
    #     return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShoppingCartListSerializer(instance, context=self.context).data


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order representation."""

    customer = serializers.ReadOnlyField(source="shopping_cart.user.username")
    # user_last_name = serializers.ReadOnlyField(source=user.last_name)
    # user_phone_number = serializers.ReadOnlyField(source=user.phone_number)
    
    class Meta:
        fields = (
            "id",
            "customer",
            "order_number",
            "ordering_date",
            "status",
            "is_paid",
            "delivery_method",
        )
        model = Order


class OrderPostDeleteSerializer(serializers.ModelSerializer):
    """Serializer for create/update/delete order."""

    order_number = serializers.SerializerMethodField()
    package = serializers.BooleanField()
    total_price = serializers.SerializerMethodField()
    address = serializers.CharField()

    class Meta:
        model = Order
        fields = "__all__"

    def validate_address(self, obj):
        if obj.delivery_method == "By courier" and not obj.address:
            raise serializers.ValidationError("Нужно указать адрес доставки!")
        return address

    def validate_package(self, obj):
        if obj.delivery_method == "By courier":
            return True

    def get_order_number(self, obj):
        number = obj.shopping_cart
        return number

    def get_total_price(self, obj):
        if self.package:
            obj.total_price += 10
        return obj.total_price

    @transaction.atomic
    def create(self, validated_data):
        order_number = validated_data.pop("order_number")
        status = validated_data.pop("status")
        delivery_method = validated_data.pop("delivery_method")
        package = validated_data.pop("package")
        order = Order.objects.create(
            order_number=order_number,
            status=status,
            delivery_method=delivery_method,
            package=package,
            user=self.context["request"].user,
        )

        status = "Ordered"
        ShoppingCartProducts.objects.bulk_create(
            [
                ShoppingCart(
                    shopping_cart=instance,
                    status=status,
                    price=Product.objects.get(price=product["price"]),
                )
                for product in products
            ]
        )
        super().update(instance, validated_data)

        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        status = validated_data.pop("status")

        return super().update(instance, status)

    def to_representation(self, instance):
        return OrderListSerializer(instance, context=self.context).data
