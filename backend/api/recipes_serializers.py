from django.db.models import F
from rest_framework import serializers

from api.products_serializers import ProductSerializer
from recipes.models import ProductsInRecipe, Recipe


class ProductLightSerializer(ProductSerializer):
    """Serializer for products representation in favorite product serializer."""

    class Meta(ProductSerializer.Meta):
        fields = ("name", "measure_unit")


class ProductsInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for products in recipe representation recipe serializer."""

    ingredient = ProductLightSerializer()

    class Meta:
        model = ProductsInRecipe
        fields = ("id", "ingredient", "amount")


# TODO: Implement ingredient output via serializer ProductsInRecipeSerializer
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe representation."""

    ingredients = serializers.SerializerMethodField()
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

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            "id",
            "name",
            "measure_unit",
            quantity=F("productsinrecipe__amount"),
        )
        return ingredients

    def get_total_ingredients(self, obj):
        return obj.ingredients.count()

    def get_recipe_nutrients(self, obj):
        proteins = 0
        fats = 0
        carbohydrates = 0

        for ingredient in obj.ingredients.all():
            proteins += (
                ingredient.proteins * ingredient.productsinrecipe.get().amount
            ) / 100
            fats += (ingredient.fats * ingredient.productsinrecipe.get().amount) / 100
            carbohydrates += (
                ingredient.carbohydrates * ingredient.productsinrecipe.get().amount
            ) / 100
        kcal = proteins * 4 + fats * 9 + carbohydrates * 4

        return {
            "proteins": proteins,
            "fats": fats,
            "carbohydrates": carbohydrates,
            "kcal": kcal,
        }
