from django.contrib import admin

from .models import ProductsInRecipe, Recipe


class RecipeIngredientInline(admin.TabularInline):
    model = ProductsInRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Class to display recipes in admin panel."""

    list_display = (
        "pk",
        "name",
        "author",
        "text",
        "pub_date",
    )
    fields = (
        "name",
        "author",
        "text",
        "cooking_time",
        "pub_date",
    )
    list_display_links = ("name",)
    search_fields = (
        "author__username",
        "name",
    )
    list_filter = (
        "author",
        "name",
        "pub_date",
    )
    readonly_fields = ("pub_date",)
    empty_value_display = "-empty-"
    inlines = (RecipeIngredientInline,)


@admin.register(ProductsInRecipe)
class ProductsInRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_display_links = ("recipe", "ingredient")
    empty_value_display = "-empty-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("recipe").prefetch_related("ingredient")
