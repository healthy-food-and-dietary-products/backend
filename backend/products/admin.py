from django.contrib import admin

from .models import Category, Component, Producer, Promotion, Subcategory, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Class to display categories in admin panel."""

    list_display = ["pk", "name", "slug"]
    fields = ["name", "slug"]
    search_fields = ["name", "slug"]
    ordering = ["name"]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Class to display subcategories in admin panel."""

    list_display = ["pk", "parent_category", "name", "slug"]
    fields = ["parent_category", "name", "slug"]
    search_fields = ["name", "slug"]
    list_filter = ["parent_category"]
    ordering = ["name"]


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Class to display product components in admin panel."""

    list_display = ["pk", "name"]
    fields = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Class to display product tags in admin panel."""

    list_display = ["pk", "name", "slug"]
    fields = ["name", "slug"]
    search_fields = ["name", "slug"]
    ordering = ["name"]


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    """Class to display product producers in admin panel."""

    list_display = ["pk", "producer_type", "name", "address", "description"]
    fields = ["producer_type", "name", "address", "description"]
    search_fields = ["name", "address", "description"]
    ordering = ["name"]
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
    ordering = ["name"]
    list_filter = ["promotion_type", "is_active", "is_constant"]
    empty_value_display = "-empty-"  # not shown
