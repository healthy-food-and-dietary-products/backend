from django.contrib import admin
from django.db.models import Avg, Count

from .models import (
    Category,
    Component,
    Coupon,
    FavoriteProduct,
    Producer,
    Product,
    ProductPromotion,
    Promotion,
    Subcategory,
    Tag,
)
from api.products_serializers import RATING_DECIMAL_PLACES
from orders.models import Order
from reviews.models import Review


class CategorySubcategoriesInline(admin.TabularInline):
    """Inline class to display subcategories of a category."""

    model = Subcategory
    extra = 0


class ComponentProductInline(admin.TabularInline):
    """Built-in class for displaying products containing a given component."""

    model = Product.components.through
    readonly_fields = ["product"]
    can_delete = False
    extra = 0


class ProductPromotionsInline(admin.TabularInline):
    """Inline class to display promotions of a product."""

    model = ProductPromotion
    readonly_fields = ["promotion"]
    can_delete = False
    extra = 0


class ProductFavoritesInline(admin.TabularInline):
    """Inline class to display favorites of a product."""

    model = FavoriteProduct
    readonly_fields = ["user"]
    can_delete = False
    extra = 0


class ProductReviewInline(admin.TabularInline):
    """Inline class to display reviews of a product."""

    model = Review
    readonly_fields = ["score", "text", "author", "was_edited"]
    can_delete = False
    extra = 0


class PromotionProductInline(admin.TabularInline):
    """
    Inline class to display the number of products to which this promotion is applied.
    """

    model = ProductPromotion
    readonly_fields = ["product"]
    extra = 0


class CouponOrderInline(admin.TabularInline):
    """Inline class to display the number of orders to which this coupon is applied."""

    model = Order
    fields = [
        "order_number",
        "user",
        "status",
        "is_paid",
        "payment_method",
        "delivery_method",
        "total_price",
    ]
    readonly_fields = [
        "order_number",
        "user",
        "status",
        "is_paid",
        "payment_method",
        "delivery_method",
        "total_price",
    ]
    can_delete = False
    extra = 0


class UserFavoritesInline(admin.TabularInline):
    """Inline class to display favorites of a user."""

    model = FavoriteProduct
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Class to display categories in admin panel."""

    list_display = ["pk", "name", "slug", "number_subcategories", "products_count"]
    list_display_links = ["name"]
    search_fields = ["name", "slug"]
    readonly_fields = ["number_subcategories", "products_count"]
    ordering = ["pk"]
    inlines = [CategorySubcategoriesInline]

    @admin.display(description="Subcategories count", ordering="number_subcategories")
    def number_subcategories(self, obj):
        """Shows the number of subcategories for this category."""
        return obj.number_subcategories

    @admin.display(description="Products count", ordering="products_count")
    def products_count(self, obj):
        """Shows the number of products for this category."""
        return obj.products_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("subcategories", "products").annotate(
            products_count=Count("products", distinct=True),
            number_subcategories=Count("subcategories", distinct=True),
        )


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Class to display subcategories in admin panel."""

    list_display = ["pk", "name", "slug", "parent_category", "products_count"]
    list_display_links = ["name"]
    readonly_fields = ["products_count"]
    search_fields = ["name", "slug"]
    list_filter = ["parent_category"]
    ordering = ["pk"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("products").annotate(
            products_count=Count("products", distinct=True)
        )

    @admin.display(description="Products count", ordering="products_count")
    def products_count(self, obj):
        """Shows the number of products for this subcategory."""
        return obj.products_count


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Class to display product components in admin panel."""

    list_display = ["pk", "name", "slug", "products_count"]
    list_display_links = ["name"]
    readonly_fields = ["products_count"]
    search_fields = ["name"]
    ordering = ["pk"]
    inlines = [ComponentProductInline]

    @admin.display(description="Products count", ordering="products_count")
    def products_count(self, obj):
        """Shows the number of products for this component."""
        return obj.products_count

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("products")
            .annotate(products_count=Count("products", distinct=True))
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Class to display product tags in admin panel."""

    list_display = ["pk", "name", "slug", "products_count"]
    list_display_links = ["name"]
    readonly_fields = ["products_count"]
    search_fields = ["name", "slug"]
    ordering = ["pk"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("products").annotate(
            products_count=Count("products", distinct=True)
        )

    @admin.display(description="Products count", ordering="products_count")
    def products_count(self, obj):
        """Shows the number of products for this tag."""
        return obj.products_count


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    """Class to display product producers in admin panel."""

    list_display = [
        "pk",
        "producer_type",
        "name",
        "slug",
        "address",
        "description",
        "products_count",
    ]
    list_display_links = ["name"]
    readonly_fields = ["products_count"]
    search_fields = ["name", "slug", "address", "description"]
    ordering = ["pk"]
    list_filter = ["producer_type"]
    empty_value_display = "-empty-"

    @admin.display(description="Products count", ordering="products_count")
    def products_count(self, obj):
        """Shows the number of products for this producer."""
        return obj.products_count

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("products")
            .annotate(products_count=Count("products", distinct=True))
        )


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
        "products_count",
    ]
    list_display_links = ["name"]
    readonly_fields = ["products_count"]
    search_fields = ["name", "discount", "conditions", "start_time", "end_time"]
    ordering = ["pk"]
    list_filter = ["promotion_type", "is_active", "is_constant"]
    empty_value_display = "-empty-"
    inlines = [PromotionProductInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("products")
            .annotate(products_count=Count("products", distinct=True))
        )

    @admin.display(description="Products count", ordering="products_count")
    def products_count(self, obj):
        """Shows the number of products to which this coupon is applied."""
        return obj.products_count


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Class to display coupons in admin panel."""

    list_display = [
        "pk",
        "name",
        "code",
        "slug",
        "promotion_type",
        "discount",
        "is_active",
        "is_constant",
        "start_time",
        "end_time",
        "orders_count",
    ]
    readonly_fields = ["orders_count"]
    list_display_links = ["code"]
    search_fields = ["name", "code", "discount", "conditions", "start_time", "end_time"]
    ordering = ["pk"]
    list_filter = ["promotion_type", "is_active", "is_constant"]
    empty_value_display = "-empty-"
    inlines = [CouponOrderInline]

    def get_changeform_initial_data(self, request):
        return {"promotion_type": Promotion.COUPON}

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("orders")
            .annotate(orders_count=Count("orders", distinct=True))
        )

    @admin.display(description="Orders count", ordering="orders_count")
    def orders_count(self, obj):
        """Shows the number of orders to which this coupon is applied."""
        return obj.orders_count


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Class to display products in admin panel."""

    list_display = [
        "pk",
        "name",
        "category",
        "discontinued",
        "price",
        "final_price",
        "rating",
        "views_number",
        "orders_number",
        "favorites_count",
        "reviews_count",
    ]
    list_display_links = ["name"]
    search_fields = ["name", "description", "producer__name"]
    readonly_fields = [
        "creation_time",
        "promotion_quantity",
        "final_price",
        "rating",
        "favorites_count",
        "reviews_count",
    ]
    ordering = ["pk"]
    list_filter = [
        "category",
        "tags",
        "subcategory",
        "discontinued",
        "producer",
        "measure_unit",
    ]
    inlines = [ProductPromotionsInline, ProductFavoritesInline, ProductReviewInline]
    empty_value_display = "-empty-"

    @admin.display(description="Number of promotions")
    def promotion_quantity(self, obj):
        """Shows the number of promotions for this product."""
        return obj.promotion_quantity

    @admin.display(description="Favorites count", ordering="favorites_count")
    def favorites_count(self, obj):
        """Shows the number of favorites for this product."""
        return obj.favorites_count

    @admin.display(description="Reviews count", ordering="reviews_count")
    def reviews_count(self, obj):
        """Shows the number of reviews of this product."""
        return obj.reviews_count

    @admin.display(description="Rating", ordering="rating")
    def rating(self, obj):
        """Shows the product rating."""
        return (
            round(obj.rating, RATING_DECIMAL_PLACES)
            if obj.rating is not None
            else obj.rating
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return (
            queryset.select_related("category", "subcategory", "producer")
            .prefetch_related(
                "components", "tags", "promotions", "reviews", "favorites"
            )
            .annotate(
                promotion_quantity=Count("promotions", distinct=True),
                favorites_count=Count("favorites", distinct=True),
                reviews_count=Count("reviews", distinct=True),
                rating=Avg("reviews__score"),
            )
        )


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    """Class to display connections between products and promotions."""

    list_display = ["pk", "promotion", "product"]
    list_display_links = ["promotion"]
    fields = ["promotion", "product"]


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    """Class to display favorite products of users in admin panel."""

    list_display = ["pk", "product", "user"]
    list_display_links = ["product"]
    fields = ["user", "product"]
    search_fields = ["user__username", "product__name"]
    list_filter = ["product"]
