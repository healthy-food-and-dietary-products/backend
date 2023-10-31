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

    subcategory_name = serializers.CharField(source="name")

    class Meta:
        model = Subcategory
        fields = ("subcategory_name",)


class SubcategorySerializer(SubcategoryLightSerializer):
    """Serializer for subcategories representation."""

    class Meta(SubcategoryLightSerializer.Meta):
        fields = ("id", "parent_category", "name", "slug")


class CategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for categories representation in product serializer."""

    category_name = serializers.CharField(source="name")

    class Meta:
        model = Category
        fields = ("category_name",)


class CategoryCreateSerializer(CategoryLightSerializer):
    """Serializer for creating categories."""

    class Meta:
        model = Category
        fields = ("category_name", "slug")


class CategorySerializer(CategoryLightSerializer):
    """Serializer for displaying categories."""

    subcategories = SubcategoryLightSerializer(many=True, required=False)

    class Meta(CategoryLightSerializer.Meta):
        fields = ("id", "name", "slug", "subcategories")


class TagLightSerializer(serializers.ModelSerializer):
    """Serializer for tags representation in product serializer."""

    tag_name = serializers.CharField(source="name")

    class Meta:
        model = Tag
        fields = ("tag_name",)


class TagSerializer(TagLightSerializer):
    """Serializer for tags representation."""

    class Meta(TagLightSerializer.Meta):
        fields = ("id", "name", "slug")


class ComponentLightSerializer(serializers.ModelSerializer):
    """Serializer for components representation in product serializer."""

    component_name = serializers.CharField(source="name")

    class Meta:
        model = Component
        fields = ("component_name",)


class ComponentSerializer(ComponentLightSerializer):
    """Serializer for components representation."""

    class Meta(ComponentLightSerializer.Meta):
        fields = ("id", "name")


class ProducerLightSerializer(serializers.ModelSerializer):
    """Serializer for produsers representation in product serializer."""

    producer_name = serializers.CharField(source="name")

    class Meta:
        model = Producer
        fields = ("producer_name",)


class ProducerSerializer(ProducerLightSerializer):
    """Serializer for produsers representation."""

    class Meta(ProducerLightSerializer.Meta):
        fields = ("id", "name", "slug", "producer_type", "description", "address")


class PromotionLightSerializer(serializers.ModelSerializer):
    """Serializer for promotions representation in product serializer."""

    promotion_name = serializers.CharField(source="name")

    class Meta:
        model = Promotion
        fields = ("promotion_name", "discount")


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

    def validate_discount(self, value):
        """Checks that the discount is between 0 and 100%."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Допустимы числа от 0 до 100.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for displaying products."""

    category = CategoryLightSerializer(read_only=True)
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

    category = serializers.PrimaryKeyRelatedField(read_only=True)
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
