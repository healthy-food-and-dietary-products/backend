from django.db.models import Avg
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .users_serializers import UserLightSerializer
from products.models import (
    MAX_PROMOTIONS_NUMBER,
    Category,
    Component,
    FavoriteProduct,
    Producer,
    Product,
    ProductPromotion,
    Promotion,
    Subcategory,
    Tag,
)

NO_RATING_MESSAGE = "У данного продукта еще нет оценок."


class SubcategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for subcategories representation in product serializer."""

    subcategory_name = serializers.CharField(source="name")
    subcategory_slug = serializers.CharField(source="slug")

    class Meta:
        model = Subcategory
        fields = ("subcategory_name", "subcategory_slug")


class SubcategorySerializer(SubcategoryLightSerializer):
    """Serializer for subcategories representation."""

    class Meta(SubcategoryLightSerializer.Meta):
        fields = ("id", "parent_category", "name", "slug", "image")


class CategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for categories representation in product serializer."""

    category_name = serializers.CharField(source="name")
    category_slug = serializers.CharField(source="slug")

    class Meta:
        model = Category
        fields = ("category_name", "category_slug")


class CategoryCreateSerializer(CategoryLightSerializer):
    """Serializer for creating categories."""

    class Meta:
        model = Category
        fields = ("id", "category_name", "slug", "image")


class CategorySerializer(CategoryLightSerializer):
    """Serializer for displaying categories."""

    subcategories = SubcategoryLightSerializer(many=True, required=False)
    top_three_products = serializers.SerializerMethodField()

    class Meta(CategoryLightSerializer.Meta):
        fields = ("id", "name", "slug", "image", "subcategories", "top_three_products")

    def get_top_three_products(self, obj):
        """Shows three most popular products of a particular category."""
        top_three_products_queryset = (
            obj.products.select_related("category", "subcategory", "producer")
            .prefetch_related("components", "tags", "promotions", "reviews")
            .order_by("-orders_number")[:3]
        )
        return ProductSerializer(
            top_three_products_queryset, many=True, context=self.context
        ).data


class TagLightSerializer(serializers.ModelSerializer):
    """Serializer for tags representation in product serializer."""

    tag_name = serializers.CharField(source="name")
    tag_slug = serializers.CharField(source="slug")

    class Meta:
        model = Tag
        fields = ("tag_name", "tag_slug")


class TagSerializer(TagLightSerializer):
    """Serializer for tags representation."""

    top_three_products = serializers.SerializerMethodField()

    class Meta(TagLightSerializer.Meta):
        fields = ("id", "name", "slug", "image", "top_three_products")

    def get_top_three_products(self, obj):
        """Shows three most popular products of a particular tag."""
        top_three_products_queryset = (
            obj.products.select_related("category", "subcategory", "producer")
            .prefetch_related("components", "tags", "promotions", "reviews")
            .order_by("-orders_number")[:3]
        )
        return ProductSerializer(
            top_three_products_queryset, context=self.context, many=True
        ).data


class ComponentLightSerializer(serializers.ModelSerializer):
    """Serializer for components representation in product serializer."""

    component_name = serializers.CharField(source="name")
    component_slug = serializers.CharField(source="slug")

    class Meta:
        model = Component
        fields = ("component_name", "component_slug")


class ComponentSerializer(ComponentLightSerializer):
    """Serializer for components representation."""

    class Meta(ComponentLightSerializer.Meta):
        fields = ("id", "name", "slug")


class ProducerLightSerializer(serializers.ModelSerializer):
    """Serializer for produsers representation in product serializer."""

    producer_name = serializers.CharField(source="name")
    producer_slug = serializers.CharField(source="slug")

    class Meta:
        model = Producer
        fields = ("producer_name", "producer_slug")


class ProducerSerializer(ProducerLightSerializer):
    """Serializer for produsers representation."""

    class Meta(ProducerLightSerializer.Meta):
        fields = (
            "id",
            "name",
            "slug",
            "producer_type",
            "description",
            "address",
            "image",
        )


class PromotionLightSerializer(serializers.ModelSerializer):
    """Serializer for promotions representation in product serializer."""

    promotion_name = serializers.CharField(source="name")
    promotion_slug = serializers.CharField(source="slug")

    class Meta:
        model = Promotion
        fields = ("promotion_name", "promotion_slug", "discount")


class PromotionSerializer(ProducerLightSerializer):
    """Serializer for promotions representation."""

    class Meta(PromotionLightSerializer.Meta):
        fields = (
            "id",
            "promotion_type",
            "name",
            "slug",
            "discount",
            "conditions",
            "is_active",
            "is_constant",
            "start_time",
            "end_time",
            "image",
        )

    def validate_discount(self, value):
        """Checks that the discount is between 0 and 100%."""
        if value < 0 or value > 100:
            raise serializers.ValidationError(Promotion.INVALID_DISCOUNT_MESSAGE)
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
    photo = serializers.ImageField(required=False)
    final_price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

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
            "rating",
            "components",
            "kcal",
            "proteins",
            "fats",
            "carbohydrates",
            "views_number",
            "orders_number",
            "is_favorited",
        )

    @extend_schema_field(bool)
    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.is_favorited(request.user)

    @extend_schema_field(int)
    def get_promotion_quantity(self, obj):
        return obj.promotions.count()

    @extend_schema_field(float)
    def get_final_price(self, obj):
        return obj.final_price

    def get_rating(self, obj):
        product_reviews = obj.reviews.all()
        if product_reviews:
            return round(product_reviews.aggregate(Avg("score"))["score__avg"], 1)
        return NO_RATING_MESSAGE


class ProductCreateSerializer(ProductSerializer):
    """Serializer for creating products."""

    PRICE_ERROR_MESSAGE = "Отрицательная цена недопустима."

    category = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())
    producer = serializers.PrimaryKeyRelatedField(queryset=Producer.objects.all())
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=False
    )
    components = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Component.objects.all()
    )

    class Meta(ProductSerializer.Meta):
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
            "photo",
            "components",
            "kcal",
            "proteins",
            "fats",
            "carbohydrates",
        )

    # TODO: This error message is not displayed, another error message is displayed
    def validate_price(self, value):
        """Checks that the price is more or equals to 0."""
        if value < 0:
            raise serializers.ValidationError(self.PRICE_ERROR_MESSAGE)
        return value


class ProductUpdateSerializer(ProductCreateSerializer):
    """Serializer for updating products."""

    promotions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Promotion.objects.all()
    )

    class Meta(ProductSerializer.Meta):
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
            "photo",
            "components",
            "kcal",
            "proteins",
            "fats",
            "carbohydrates",
        )

    def validate_promotions(self, value):
        """Checks the number of promotions that apply to a product."""
        if len(value) > MAX_PROMOTIONS_NUMBER:
            raise serializers.ValidationError(
                ProductPromotion.MAX_PROMOTIONS_ERROR_MESSAGE
            )
        return value


class ProductPresentSerializer(serializers.ModelSerializer):
    """Serializer for short presentation products."""

    photo = serializers.ImageField(required=False)
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "measure_unit",
            "amount",
            "final_price",
            "photo",
            "category"
        )

    @extend_schema_field(float)
    def get_final_price(self, obj):
        return obj.final_price


class ProductLightSerializer(ProductSerializer):
    """Serializer for products representation in favorite product serializer."""

    class Meta(ProductSerializer.Meta):
        fields = ("name",)


class FavoriteProductSerializer(serializers.ModelSerializer):
    """Serializer for favorite products list representation."""

    product = ProductLightSerializer()
    user = UserLightSerializer()

    class Meta:
        model = FavoriteProduct
        fields = ("id", "user", "product")


class FavoriteProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creation favorite products."""

    class Meta:
        model = FavoriteProduct
        fields = ("id",)
