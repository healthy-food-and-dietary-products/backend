from math import ceil

from django.db.models import Count, F, Prefetch, Sum
from drf_yasg import openapi
from rest_framework import serializers

from products.models import Product
from recipes.models import ProductsInRecipe, Recipe

RECIPE_KCAL_DECIMAL_PLACES = 0
RECIPE_NUTRIENTS_DECIMAL_PLACES = 1


class ProductsInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for products in recipe representation recipe serializer."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measure_unit = serializers.ReadOnlyField(source="ingredient.measure_unit")
    amount = serializers.ReadOnlyField(source="ingredient.amount")
    final_price = serializers.ReadOnlyField(source="ingredient.final_price")
    ingredient_photo = serializers.ImageField(source="ingredient.photo")
    quantity_in_recipe = serializers.ReadOnlyField(source="amount")
    need_to_buy = serializers.SerializerMethodField()

    class Meta:
        model = ProductsInRecipe
        fields = (
            "id",
            "name",
            "measure_unit",
            "amount",
            "final_price",
            "ingredient_photo",
            "quantity_in_recipe",
            "need_to_buy",
        )
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "properties": {
                "id": openapi.Schema(
                    title="ID", type=openapi.TYPE_INTEGER, read_only=True
                ),
                "name": openapi.Schema(
                    title="Name",
                    type=openapi.TYPE_STRING,
                    read_only=True,
                ),
                "measure_unit": openapi.Schema(
                    title="Measure unit",
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        enum=[Product.GRAMS, Product.MILLILITRES, Product.ITEMS],
                        type=openapi.TYPE_STRING,
                    ),
                    read_only=True,
                ),
                "amount": openapi.Schema(
                    title="Amount",
                    type=openapi.TYPE_INTEGER,
                    read_only=True,
                ),
                "final_price": openapi.Schema(
                    title="Final price",
                    type=openapi.TYPE_NUMBER,
                    read_only=True,
                ),
                "ingredient_photo": openapi.Schema(
                    title="Ingredient photo",
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_URI,
                    read_only=True,
                ),
                "quantity_in_recipe": openapi.Schema(
                    title="Quantity in recipe",
                    type=openapi.TYPE_INTEGER,
                    read_only=True,
                ),
                "need_to_buy": openapi.Schema(
                    title="Need to buy",
                    type=openapi.TYPE_INTEGER,
                    read_only=True,
                ),
            },
        }

    def get_need_to_buy(self, obj) -> int:
        """Calculates the number of product units to buy for this recipe."""
        return ceil(obj.amount / obj.ingredient.amount)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe representation."""

    ingredients = ProductsInRecipeSerializer(source="recipeingredient", many=True)
    total_ingredients = serializers.SerializerMethodField()
    proteins = serializers.SerializerMethodField()
    fats = serializers.SerializerMethodField()
    carbohydrates = serializers.SerializerMethodField()
    kcal = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "text",
            "image",
            "ingredients",
            "total_ingredients",
            "proteins",
            "fats",
            "carbohydrates",
            "kcal",
            "cooking_time",
        )

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Perform necessary eager loading of recipes data."""
        return queryset.prefetch_related(
            Prefetch(
                "recipeingredient",
                queryset=ProductsInRecipe.objects.select_related(
                    "ingredient"
                ).prefetch_related("ingredient__promotions"),
            )
        ).annotate(
            total_ingredients=Count("ingredients"),
            proteins=Sum(
                F("recipeingredient__ingredient__proteins")
                * F("recipeingredient__amount")
                / 100
            ),
            fats=Sum(
                F("recipeingredient__ingredient__fats")
                * F("recipeingredient__amount")
                / 100
            ),
            carbohydrates=Sum(
                F("recipeingredient__ingredient__carbohydrates")
                * F("recipeingredient__amount")
                / 100
            ),
            kcal=F("proteins") * 4 + F("fats") * 9 + F("carbohydrates") * 4,
        )

    def get_proteins(self, obj) -> float:
        return round(obj.proteins, RECIPE_NUTRIENTS_DECIMAL_PLACES)

    def get_fats(self, obj) -> float:
        return round(obj.fats, RECIPE_NUTRIENTS_DECIMAL_PLACES)

    def get_carbohydrates(self, obj) -> float:
        return round(obj.carbohydrates, RECIPE_NUTRIENTS_DECIMAL_PLACES)

    def get_kcal(self, obj) -> int:
        return round(obj.kcal, RECIPE_KCAL_DECIMAL_PLACES)

    def get_total_ingredients(self, obj) -> int:
        return obj.total_ingredients
