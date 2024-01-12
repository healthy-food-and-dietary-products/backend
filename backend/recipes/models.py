from django.core.validators import MinValueValidator
from django.db import models

from core.models import CreatedModel
from products.models import Product
from users.models import User


class Recipe(CreatedModel):
    """A model for recipes.

    It is described by the following fields:

    author - The author of the recipe (user).
    name - The name of the recipe.
    image - Picture of the finished dish.
    text - Text description of the recipe.
    ingredients - Ingredients: products for cooking the dish according to the recipe.
    Multiple field, selection from a list of products,
    with the quantity.
    cooking_time - Cooking time in minutes.
    """

    def recipe_directory_path(self, filename):
        """Constructs the path which the product photo will be saved."""
        return f"images/recipes/{self.pk}.jpg"

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Recipe author",
        related_name="recipes",
    )
    name = models.CharField(
        "Recipe title",
        max_length=255,
    )
    image = models.ImageField("Dish image", blank=True, upload_to=recipe_directory_path)
    text = models.TextField(
        "Recipe description",
    )
    ingredients = models.ManyToManyField(
        Product,
        related_name="recipes",
        verbose_name="Ingredients",
        through="ProductsInRecipe",
    )
    cooking_time = models.PositiveIntegerField(
        "Cooking time",
        validators=[MinValueValidator(1)],
    )
    short_description = models.TextField("Short description", blank=True, null=True)
    servings_quantity = models.CharField(
        "Servings Quantity", max_length=255, blank=True, null=True
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class ProductsInRecipe(models.Model):
    """A model of the ingredients in a recipe.

    It is described by the following fields:

    ingredient - The ingredient from the product model.
    amount - The amount of the ingredient.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipeingredient",
        verbose_name="Рецепт",
    )

    ingredient = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="productsinrecipe",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return f"{self.ingredient.name}: {self.amount}"

    class Meta:
        verbose_name = "Products in recipe"
        verbose_name_plural = "Products in recipes"
