from django.db.models import Avg, Exists, OuterRef, Prefetch
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

RATING_DECIMAL_PLACES = 1


class SubcategoryLightSerializer(serializers.ModelSerializer):
    """Serializer for subcategories representation in product serializer."""

    subcategory_name = serializers.CharField(source="name")
    subcategory_slug = serializers.SlugField(source="slug")

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
    category_slug = serializers.SlugField(source="slug")

    class Meta:
        model = Category
        fields = ("category_name", "category_slug")


class CategoryCreateSerializer(CategoryLightSerializer):
    """Serializer for creating categories."""

    class Meta:
        model = Category
        fields = ("id", "category_name", "slug", "image")


class TagLightSerializer(serializers.ModelSerializer):
    """Serializer for tags representation in product serializer."""

    tag_name = serializers.CharField(source="name")
    tag_slug = serializers.SlugField(source="slug")

    class Meta:
        model = Tag
        fields = ("tag_name", "tag_slug")


class ComponentLightSerializer(serializers.ModelSerializer):
    """Serializer for components representation in product serializer."""

    component_name = serializers.CharField(source="name")
    component_slug = serializers.SlugField(source="slug")

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
    producer_slug = serializers.SlugField(source="slug")

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
    promotion_slug = serializers.SlugField(source="slug")

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

    @classmethod
    def setup_eager_loading(cls, queryset, user):
        """Perform necessary eager loading of products data."""
        if user.is_anonymous:
            return (
                queryset.select_related("category", "subcategory", "producer")
                .prefetch_related("components", "tags", "promotions", "reviews")
                .annotate(rating=Avg("reviews__score"))
            )
        return (
            queryset.select_related("category", "subcategory", "producer")
            .prefetch_related("components", "tags", "promotions", "reviews")
            .annotate(
                rating=Avg("reviews__score"),
                favorited=Exists(
                    FavoriteProduct.objects.filter(user=user, product=OuterRef("id"))
                ),
            )
        )

    @extend_schema_field(bool)
    def get_is_favorited(self, obj) -> bool:
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited

    @extend_schema_field(int)
    def get_promotion_quantity(self, obj) -> int:
        return obj.promotions.count()

    @extend_schema_field(float)
    def get_final_price(self, obj) -> float:
        return obj.final_price

    def get_rating(self, obj) -> float:
        """Rounds and returns the annotated rating value."""
        return (
            round(obj.rating, RATING_DECIMAL_PLACES)
            if obj.rating is not None
            else obj.rating
        )


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
    category = CategoryLightSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "measure_unit",
            "amount",
            "final_price",
            "photo",
            "category",
            "is_favorited",
            "orders_number",
        )

    @extend_schema_field(float)
    def get_final_price(self, obj) -> float:
        return obj.final_price

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited


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


class CategorySerializer(CategoryLightSerializer):
    """Serializer for displaying categories and their top three products."""

    subcategories = SubcategoryLightSerializer(many=True, required=False)
    top_products = ProductPresentSerializer(many=True, source="products")

    class Meta(CategoryLightSerializer.Meta):
        fields = ("id", "name", "slug", "image", "subcategories", "top_products")

    @classmethod
    def setup_eager_loading(cls, queryset, user):
        """Perform necessary eager loading of categories data."""
        if user.is_anonymous:
            return queryset.prefetch_related(
                "subcategories",
                Prefetch(
                    "products",
                    queryset=Product.objects.prefetch_related("promotions").order_by(
                        "-orders_number"
                    ),
                ),
            )
        return queryset.prefetch_related(
            "subcategories",
            Prefetch(
                "products",
                queryset=Product.objects.prefetch_related("promotions")
                .annotate(
                    favorited=Exists(
                        FavoriteProduct.objects.filter(
                            user=user, product=OuterRef("id")
                        )
                    )
                )
                .order_by("-orders_number"),
            ),
        )


class CategoryBriefSerializer(CategorySerializer):
    """Serializer for displaying brief categories information."""

    class Meta(CategorySerializer.Meta):
        fields = ("id", "name", "slug", "image")


class TagSerializer(TagLightSerializer):
    """Serializer for tags representation."""

    top_products = ProductPresentSerializer(
        many=True, source="products", required=False
    )

    class Meta(TagLightSerializer.Meta):
        fields = ("id", "name", "slug", "image", "top_products")

    @classmethod
    def setup_eager_loading(cls, queryset, user):
        """Perform necessary eager loading of tags data."""
        if user.is_anonymous:
            return queryset.prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.select_related("category")
                    .prefetch_related("promotions")
                    .order_by("-orders_number"),
                ),
            )
        return queryset.prefetch_related(
            Prefetch(
                "products",
                queryset=Product.objects.select_related("category")
                .prefetch_related("promotions")
                .annotate(
                    favorited=Exists(
                        FavoriteProduct.objects.filter(
                            user=user, product=OuterRef("id")
                        )
                    )
                )
                .order_by("-orders_number"),
            ),
        )
