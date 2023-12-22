from django.contrib import admin
from django.db.models import Avg

from .models import (
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


class CategorySubcategoriesInline(admin.TabularInline):
    """Inline class to display subcategories of a category."""

    model = Subcategory
    extra = 1


class ProductPromotionsInline(admin.TabularInline):
    """Inline class to display promotions of a product."""

    model = ProductPromotion
    readonly_fields = ["promotion"]
    can_delete = False
    extra = 1


class ProductFavoritesInline(admin.TabularInline):
    """Inline class to display favorites of a product."""

    model = FavoriteProduct
    extra = 1


class UserFavoritesInline(admin.TabularInline):
    """Inline class to display favorites of a user."""

    model = FavoriteProduct
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Class to display categories in admin panel."""

    list_display = ["pk", "name", "slug", "number_subcategories"]
    list_display_links = ("name",)
    fields = ["name", "slug", "image"]
    search_fields = ["name", "slug"]
    readonly_fields = ["number_subcategories"]
    ordering = ["pk"]
    inlines = [CategorySubcategoriesInline]

    @admin.display(description="Number of subcategories")
    def number_subcategories(self, obj):
        """Shows the number of subcategories for this category."""
        return obj.subcategories.count()


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Class to display subcategories in admin panel."""

    list_display = ["pk", "name", "slug", "parent_category"]
    list_display_links = ("name",)
    fields = ["parent_category", "name", "slug", "image"]
    search_fields = ["name", "slug"]
    list_filter = ["parent_category"]
    ordering = ["pk"]


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Class to display product components in admin panel."""

    list_display = ["pk", "name", "slug"]
    list_display_links = ("name",)
    fields = ["name", "slug"]
    search_fields = ["name"]
    ordering = ["pk"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Class to display product tags in admin panel."""

    list_display = ["pk", "name", "slug"]
    list_display_links = ("name",)
    fields = ["name", "slug", "image"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    """Class to display product producers in admin panel."""

    list_display = ["pk", "producer_type", "name", "slug", "address", "description"]
    list_display_links = ("name",)
    fields = ["producer_type", "name", "slug", "address", "description", "image"]
    search_fields = ["name", "slug", "address", "description"]
    ordering = ["pk"]
    list_filter = ["producer_type"]
    empty_value_display = "-empty-"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Class to display promotions in admin panel."""

    list_display = [
        "pk",
        "name",
        "slug",
        "promotion_type",
        "discount",
        "is_active",
        "is_constant",
        "start_time",
        "end_time",
    ]
    list_display_links = ("name",)
    fields = [
        "name",
        "slug",
        "promotion_type",
        "discount",
        "is_active",
        "is_constant",
        "start_time",
        "end_time",
        "conditions",
        "image",
    ]
    search_fields = ["name", "discount", "conditions", "start_time", "end_time"]
    ordering = ["pk"]
    list_filter = ["promotion_type", "is_active", "is_constant"]
    empty_value_display = "-empty-"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Class to display products in admin panel."""

    list_display = [
        "pk",
        "name",
        "category",
        "discontinued",
        "producer",
        "price",
        "final_price",
        "rating",
        "views_number",
        "orders_number",
    ]
    list_display_links = ("name",)
    fields = [
        "name",
        "description",
        "creation_time",
        "category",
        "subcategory",
        "tags",
        "discontinued",
        "producer",
        "price",
        "final_price",
        "rating",
        "measure_unit",
        "amount",
        "promotion_quantity",
        "components",
        "kcal",
        "proteins",
        "fats",
        "carbohydrates",
        "views_number",
        "orders_number",
        "photo",
    ]
    search_fields = ["name", "description", "producer__name"]
    readonly_fields = ["creation_time", "promotion_quantity", "final_price", "rating"]
    ordering = ["pk"]
    list_filter = [
        "category",
        "subcategory",
        "tags",
        "discontinued",
        "producer",
        "measure_unit",
    ]
    inlines = [ProductPromotionsInline, ProductFavoritesInline]
    empty_value_display = "-empty-"

    @admin.display(description="Number of promotions")
    def promotion_quantity(self, obj):
        """Shows the number of promotions for this product."""
        return obj.promotions.count()

    @admin.display(description="Rating")
    def rating(self, obj):
        """Shows the product rating."""
        product_reviews = obj.reviews.all()
        if product_reviews:
            return round(product_reviews.aggregate(Avg("score"))["score__avg"], 1)
        return "-empty-"


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    """Class to display connections between products and promotions."""

    list_display = ["pk", "promotion", "product"]
    list_display_links = ("promotion",)
    fields = ["promotion", "product"]


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    """Class to display favorite products of users in admin panel."""

    list_display = ["pk", "product", "user"]
    list_display_links = ("product",)
    fields = ["user", "product"]
    search_fields = ["user__username", "product__name"]
    list_filter = ["product"]
