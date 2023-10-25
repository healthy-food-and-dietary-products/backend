from django.contrib import admin

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
    fields = ["name", "slug"]
    search_fields = ["name", "slug"]
    readonly_fields = ["number_subcategories"]
    ordering = ["pk"]
    inlines = [CategorySubcategoriesInline]

    @admin.display(description="Number of subcategories")
    def number_subcategories(self, obj):
        return obj.subcategories.count()


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Class to display subcategories in admin panel."""

    list_display = ["pk", "name", "slug", "parent_category"]
    fields = ["parent_category", "name", "slug"]
    search_fields = ["name", "slug"]
    list_filter = ["parent_category"]
    ordering = ["pk"]


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Class to display product components in admin panel."""

    list_display = ["pk", "name"]
    fields = ["name"]
    search_fields = ["name"]
    ordering = ["pk"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Class to display product tags in admin panel."""

    list_display = ["pk", "name", "slug"]
    fields = ["name", "slug"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    """Class to display product producers in admin panel."""

    list_display = ["pk", "producer_type", "name", "address", "description"]
    fields = ["producer_type", "name", "address", "description"]
    search_fields = ["name", "address", "description"]
    ordering = ["pk"]
    list_filter = ["producer_type"]
    empty_value_display = "-empty-"  # not shown


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Class to display promotions in admin panel."""

    list_display = [
        "pk",
        "name",
        "promotion_type",
        "discount",
        "is_active",
        "is_constant",
        "start_time",
        "end_time",
    ]
    fields = [
        "name",
        "promotion_type",
        "discount",
        "is_active",
        "is_constant",
        "start_time",
        "end_time",
        "conditions",
    ]
    search_fields = ["name", "discount", "conditions", "start_time", "end_time"]
    ordering = ["pk"]
    list_filter = ["promotion_type", "is_active", "is_constant"]
    empty_value_display = "-empty-"  # not shown


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
        "promotion_quantity",
    ]
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
        # "photo",
    ]
    search_fields = ["name", "description", "producer"]
    readonly_fields = ["creation_time", "promotion_quantity", "final_price"]
    ordering = ["pk"]
    list_filter = [
        "category",
        "subcategory",
        "discontinued",
        "promotion_quantity",
        "producer",
        "measure_unit",
    ]
    inlines = [ProductPromotionsInline, ProductFavoritesInline]
    empty_value_display = "-empty-"  # not shown


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    """Class to display connections between products and promotions."""

    list_display = ["pk", "promotion", "product"]
    fields = ["promotion", "product"]


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    """Class to display favorite products of users in admin panel."""

    list_display = ["pk", "user", "product"]
    fields = ["user", "product"]
    search_fields = ["user", "product"]
    list_filter = ["product"]
