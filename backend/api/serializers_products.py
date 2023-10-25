from rest_framework import serializers

from .users_serializers import UserSerializer
from products.models import (
    Category,
    Component,
    FavoriteProduct,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)


class SubcategorySerializer(serializers.ModelSerializer):
    """Serializer for subcategories representation."""

    class Meta:
        model = Subcategory
        fields = ("id", "parent_category", "name", "slug")


class SubcategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for subcategories representation in product serializer."""

    class Meta:
        model = Subcategory
        fields = ("name",)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories representation."""

    subcategories = SubcategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "subcategories")


class CategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for categories representation in product serializer."""

    class Meta:
        model = Category
        fields = ("name",)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags representation."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class TagLightSerializer(serializers.ModelSerializer):
    """Serializer for tags representation in product serializer."""

    class Meta:
        model = Tag
        fields = ("name",)


class ComponentSerializer(serializers.ModelSerializer):
    """Serializer for components representation."""

    class Meta:
        model = Component
        fields = ("id", "name")


class ComponentLightSerializer(serializers.ModelSerializer):
    """Serializer for components representation in product serializer."""

    class Meta:
        model = Component
        fields = ("name",)


class ProducerSerializer(serializers.ModelSerializer):
    """Serializer for produsers representation."""

    class Meta:
        model = Producer
        fields = ("id", "name", "producer_type", "description", "address")


class ProducerLightSerializer(serializers.ModelSerializer):
    """Serializer for produsers representation in product serializer."""

    class Meta:
        model = Producer
        fields = ("name",)


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for promotions representation."""

    class Meta:
        model = Promotion
        fields = (
            "id",
            "promotion_type",
            "name",
            "discount",
            "conditions",
            "is_active",
            "is_constant",
            "start_time",
            "end_time",
        )


class PromotionLightSerializer(serializers.ModelSerializer):
    """Serializer for promotions representation in product serializer."""

    class Meta:
        model = Promotion
        fields = ("name", "discount")


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products representation."""

    category = CategoryLightSerializer()
    subcategory = SubcategoryLightSerializer()
    tags = TagLightSerializer(many=True)
    producer = ProducerLightSerializer()
    promotions = PromotionLightSerializer(many=True)
    components = ComponentLightSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "creation_time",
            "category",
            "subcategory",
            "tags",
            "discontinued",
            "producer",
            "measure_unit",
            "amount",
            "price",
            "final_price",
            "promotions",
            "promotion_quantity",
            "photo",
            "components",
            "kcal",
            "proteins",
            "fats",
            "carbohydrates",
            "views_number",
            "orders_number",
            "is_favorited",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.is_favorited(request.user)


class ProductLightSerializer(serializers.ModelSerializer):
    """Serializer for products representation in favorite product serializer."""

    producer = ProducerLightSerializer()

    class Meta:
        model = Product
        fields = (
            "name",
            "producer",
        )


class FavoriteProductSerializer(serializers.ModelSerializer):
    """Serializer for favorite products representation."""

    product = ProductLightSerializer()
    user = UserSerializer()

    class Meta:
        model = FavoriteProduct
        fields = ("id", "user", "product")


# add validators!
