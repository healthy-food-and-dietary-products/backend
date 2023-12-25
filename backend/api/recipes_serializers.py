from math import ceil

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


# TODO: make setup_eager_loading cls method
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe representation."""

    ingredients = ProductsInRecipeSerializer(source="recipeingredient", many=True)
    total_ingredients = serializers.SerializerMethodField()
    recipe_nutrients = serializers.SerializerMethodField()

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
            "recipe_nutrients",
            "cooking_time",
        )

    def get_total_ingredients(self, obj) -> int:
        return obj.ingredients.count()

    def get_recipe_nutrients(self, obj) -> dict[str, float]:
        proteins = 0
        fats = 0
        carbohydrates = 0

        for ingredient in obj.ingredients.all():
            amount = ingredient.productsinrecipe.get(recipe=obj).amount
            proteins += (ingredient.proteins * amount) / 100
            fats += (ingredient.fats * amount) / 100
            carbohydrates += (ingredient.carbohydrates * ingredient.amount) / 100
        kcal = proteins * 4 + fats * 9 + carbohydrates * 4

        return {
            "proteins": round(proteins, RECIPE_NUTRIENTS_DECIMAL_PLACES),
            "fats": round(fats, RECIPE_NUTRIENTS_DECIMAL_PLACES),
            "carbohydrates": round(carbohydrates, RECIPE_NUTRIENTS_DECIMAL_PLACES),
            "kcal": round(kcal, RECIPE_KCAL_DECIMAL_PLACES),
        }
