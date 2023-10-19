from orders.models import ShoppingCart
from rest_framework import serializers


class ShoppingCartListSerializer(serializers.ModelSerializer):
    """Serializer for product representation."""
    product_name = serializers.SerializerMethodField()
    product_amount = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('product_name', 'product_amount', 'product_price')

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_amount(self, obj):
        return obj.product.amount

    def get_product_price(self, obj):
        return obj.product.price


class ShoppingCartPostUpdateSerializer(serializers.ModelSerializer):
    count_of_product = serializers.IntegerField(default=1)

    class Meta:
        fields = '__all__'
        model = ShoppingCart
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'product'),
                message='Вы уже добавили этот продукт в корзину!'
            ),
        )

    def validate_count_of_product(self, data):
        if data < 1:
            raise serializers.ValidationError(
                'Количество  товара в корзине должно быть не меньше 1!')
        return data
