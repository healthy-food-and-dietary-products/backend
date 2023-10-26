from rest_framework import serializers

from .users_serializers import UserSerializer
from products.models import (
    MAX_PROMOTIONS_NUMBER,
    Category,
    Component,
    FavoriteProduct,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)


class SubcategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for subcategories representation in product serializer."""

    class Meta:
        model = Subcategory
        fields = ("name",)


class SubcategorySerializer(SubcategoryLightSerializer):
    """Serializer for subcategories representation."""

    class Meta(SubcategoryLightSerializer.Meta):
        fields = ("id", "parent_category", "name", "slug")


class CategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for categories representation in product serializer."""

    class Meta:
        model = Category
        fields = ("name",)


class CategorySerializer(CategoryLightSerializer):
    """Serializer for categories representation."""
    # TODO: make possible to create subcategories during the category creation

    subcategories = SubcategorySerializer(many=True)

    class Meta(CategoryLightSerializer.Meta):
        fields = ("id", "name", "slug", "subcategories")


class TagLightSerializer(serializers.ModelSerializer):
    """Serializer for tags representation in product serializer."""

    class Meta:
        model = Tag
        fields = ("name",)


class TagSerializer(TagLightSerializer):
    """Serializer for tags representation."""

    class Meta(TagLightSerializer.Meta):
        fields = ("id", "name", "slug")


class ComponentLightSerializer(serializers.ModelSerializer):
    """Serializer for components representation in product serializer."""

    class Meta:
        model = Component
        fields = ("name",)


class ComponentSerializer(ComponentLightSerializer):
    """Serializer for components representation."""

    class Meta(ComponentLightSerializer.Meta):
        fields = ("id", "name")


class ProducerLightSerializer(serializers.ModelSerializer):
    """Serializer for produsers representation in product serializer."""

    class Meta:
        model = Producer
        fields = ("name",)


class ProducerSerializer(ProducerLightSerializer):
    """Serializer for produsers representation."""

    class Meta(ProducerLightSerializer.Meta):
        fields = ("id", "name", "producer_type", "description", "address")


class PromotionLightSerializer(serializers.ModelSerializer):
    """Serializer for promotions representation in product serializer."""

    class Meta:
        model = Promotion
        fields = ("name", "discount")


class PromotionSerializer(ProducerLightSerializer):
    """Serializer for promotions representation."""

    class Meta(PromotionLightSerializer.Meta):
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


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for displaying products."""

    category = CategoryLightSerializer()
    subcategory = SubcategoryLightSerializer()
    tags = TagLightSerializer(many=True, required=False)
    producer = ProducerLightSerializer()
    promotions = PromotionLightSerializer(many=True, required=False)
    components = ComponentLightSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    promotion_quantity = serializers.SerializerMethodField()

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

    def get_promotion_quantity(self, obj):
        return obj.promotions.count()


class ProductCreateSerializer(ProductSerializer):
    """Serializer for creating products."""

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())
    producer = serializers.PrimaryKeyRelatedField(queryset=Producer.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    components = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Component.objects.all()
    )
    promotions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Promotion.objects.all()
    )

    def validate_promotions(self, value):
        """Checks that no promotions are applied to the product during its creation."""
        if value:
            raise serializers.ValidationError(
                "Promotions cannot be applied to a product during its creation."
            )
        return value


class ProductUpdateSerializer(ProductCreateSerializer):
    """Serializer for updating products."""

    def validate_promotions(self, value):
        """Checks the number of promotions that apply to a product."""
        if len(value) > MAX_PROMOTIONS_NUMBER:
            raise serializers.ValidationError(
                "The number of promotions for one product "
                f"cannot exceed {MAX_PROMOTIONS_NUMBER}."
            )
        return value


class ProductLightSerializer(ProductSerializer):
    """Serializer for products representation in favorite product serializer."""

    class Meta(ProductSerializer.Meta):
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


# TODO: add more validators!
