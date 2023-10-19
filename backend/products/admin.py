from django.contrib import admin

from .models import Category, Component, Subcategory, Tag


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
