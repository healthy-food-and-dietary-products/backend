import os
from csv import DictReader

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.utils import timezone

from good_food.settings import BASE_DIR
from recipes.models import ProductsInRecipe, Recipe

DATA_DIR = os.path.join(BASE_DIR, "data")


def read_recipes():
    with open(os.path.join(DATA_DIR, "recipes.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            if row.get("pub_date"):
                pub_date = row["pub_date"]
            else:
                pub_date = timezone.now()
            recipe = Recipe(
                id=row["id"],
                pub_date=pub_date,
                author_id=row["author_id"],
                name=row["name"],
                image=row["image"],
                text=row["text"],
                cooking_time=row["cooking_time"],
            )
            recipe.save()


def read_products_in_recipes():
    with open(
        os.path.join(DATA_DIR, "products_in_recipe.csv"), "r", encoding="utf-8"
    ) as f:
        reader = DictReader(f)
        for row in reader:
            recipe = ProductsInRecipe(
                id=row["id"],
                recipe_id=row["recipe_id"],
                ingredient_id=row["ingredient_id"],
                amount=row["amount"],
            )
            recipe.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        read_recipes()
        self.stdout.write("Данные из файла recipes.csv загружены")
        read_products_in_recipes()
        self.stdout.write("Данные из файла products_in_recipe.csv загружены")

        model_list = [ProductsInRecipe, Recipe]
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), model_list)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
