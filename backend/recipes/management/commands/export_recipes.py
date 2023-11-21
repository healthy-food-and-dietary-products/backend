import csv
import os

from django.apps import apps
from django.core.management.base import BaseCommand

from good_food.settings import BASE_DIR

DATA_DIR = os.path.join(BASE_DIR, "export")


def export_recipes():
    data = apps.get_model("recipes", "Recipe")
    field_names = [
        "id",
        "pub_date",
        "name",
        "image",
        "text",
        "cooking_time",
        "author_id",
    ]
    with open(
        os.path.join(DATA_DIR, "recipes.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_products_in_recipe():
    data = apps.get_model("recipes", "ProductsInRecipe")
    field_names = ["id", "amount", "ingredient_id", "recipe_id"]
    with open(
        os.path.join(DATA_DIR, "products_in_recipe.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


class Command(BaseCommand):
    def handle(self, *args, **options):
        export_recipes()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Recipe прошёл успешно!")
        )
        export_products_in_recipe()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели ProductsInRecipe прошёл успешно!")
        )
