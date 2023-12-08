from rest_framework import serializers

from recipes.models import ProductsInRecipe, Recipe


class ProductsInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for products in recipe representation recipe serializer."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measure_unit = serializers.ReadOnlyField(source="ingredient.measure_unit")
    quantity = serializers.ReadOnlyField(source="amount")

    class Meta:
        model = ProductsInRecipe
        fields = ("id", "name", "measure_unit", "quantity")


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

    def get_total_ingredients(self, obj):
        return obj.ingredients.count()

    def get_recipe_nutrients(self, obj):
        proteins = 0
        fats = 0
        carbohydrates = 0

        for ingredient in obj.ingredients.all():
            proteins += (
                ingredient.proteins * ingredient.productsinrecipe.get(recipe=obj).amount
            ) / 100
            fats += (
                ingredient.fats * ingredient.productsinrecipe.get(recipe=obj).amount
            ) / 100
            carbohydrates += (
                ingredient.carbohydrates
                * ingredient.productsinrecipe.get(recipe=obj).amount
            ) / 100
        kcal = proteins * 4 + fats * 9 + carbohydrates * 4

        return {
            "proteins": proteins,
            "fats": fats,
            "carbohydrates": carbohydrates,
            "kcal": kcal,
        }
