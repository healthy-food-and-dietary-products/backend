from django.contrib import admin

from .models import ProductsInRecipe, Recipe


class RecipeIngredientInline(admin.TabularInline):
    model = ProductsInRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Class to display recipes in admin panel."""

    list_display = [
        "pk",
        "name",
        "author",
        "short_description",
        "text",
        "cooking_time",
        "servings_quantity",
        "total_ingredients",
        "pub_date",
    ]
    list_display_links = ["name"]
    search_fields = ["author__username", "name", "short_description", "text"]
    list_filter = ["pub_date", "cooking_time", "servings_quantity"]
    readonly_fields = ["pub_date"]
    empty_value_display = "-empty-"
    ordering = ["pk"]
    inlines = [RecipeIngredientInline]

    @admin.display(description="Total ingredients")
    def total_ingredients(self, obj):
        """Shows the number of ingredients for this recipe."""
        return obj.ingredients.count()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author").prefetch_related("ingredients")


@admin.register(ProductsInRecipe)
class ProductsInRecipeAdmin(admin.ModelAdmin):
    list_display = ["pk", "recipe", "ingredient", "amount", "measure_unit"]
    list_display_links = ["recipe", "ingredient"]
    empty_value_display = "-empty-"

    @admin.display(description="Measure units")
    def measure_unit(self, obj):
        """Shows the ingredient measure_unit."""
        return obj.ingredient.measure_unit

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("recipe", "ingredient")
