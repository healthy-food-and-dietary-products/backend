import csv
import os

from django.apps import apps
from django.core.management.base import BaseCommand

from good_food.settings import BASE_DIR
from products.models import Product

products = Product.objects.all()
DATA_DIR = os.path.join(BASE_DIR, "export")


def export_products():
    data = apps.get_model("products", "Product")
    field_names = [
        "id",
        "name",
        "description",
        "creation_time",
        "photo",
        "category_id",
        "subcategory_id",
        "producer_id",
        "measure_unit",
        "amount",
        "price",
        "kcal",
        "proteins",
        "fats",
        "carbohydrates",
    ]
    with open(
        os.path.join(DATA_DIR, "products.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_products_components():
    field_names = ["id", "product_id", "component_id"]
    with open(
        os.path.join(DATA_DIR, "products_components.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        id = 0
        for product in products:
            components = product.components.all()
            for component in components:
                id += 1
                data = [id, product.pk, component.pk]
                writer.writerow(data)


def export_products_tags():
    field_names = ["id", "product_id", "tag_id"]
    with open(
        os.path.join(DATA_DIR, "products_tags.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        id = 0
        for product in products:
            tags = product.tags.all()
            for tag in tags:
                id += 1
                data = [id, product.pk, tag.pk]
                writer.writerow(data)


def export_categories():
    data = apps.get_model("products", "Category")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "category.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_subcategories():
    data = apps.get_model("products", "Subcategory")
    field_names = ["id", "name", "slug", "parent_category_id", "image"]
    with open(
        os.path.join(DATA_DIR, "subcategory.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_components():
    data = apps.get_model("products", "Component")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "components.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_tags():
    data = apps.get_model("products", "Tag")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "tags.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_producers():
    data = apps.get_model("products", "Producer")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "producer.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_promotions():
    data = apps.get_model("products", "Promotion")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "promotions.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_products_promotions():
    data = apps.get_model("products", "ProductPromotion")
    field_names = ["id", "product_id", "promotion_id"]
    with open(
        os.path.join(DATA_DIR, "products_promotions.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_users():
    data = apps.get_model("users", "User")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "users.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_user_address():
    data = apps.get_model("users", "Address")
    field_names = ["id", "address", "priority_address", "user_id"]
    with open(
        os.path.join(DATA_DIR, "user_addresses.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_delivery_points():
    data = apps.get_model("orders", "Delivery")
    field_names = [f.name for f in data._meta.fields]
    with open(
        os.path.join(DATA_DIR, "delivery_points.csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_favorites():
    data = apps.get_model("products", "FavoriteProduct")
    field_names = ["id", "product_id", "user_id"]
    with open(
        os.path.join(DATA_DIR, "favorites.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_tokens():
    data = apps.get_model("authtoken", "Token")
    field_names = ["key", "created", "user_id"]
    with open(
        os.path.join(DATA_DIR, "tokens.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_reviews():
    data = apps.get_model("reviews", "Review")
    field_names = [
        "id",
        "text",
        "score",
        "pub_date",
        "author_id",
        "product_id",
        "was_edited",
    ]
    with open(
        os.path.join(DATA_DIR, "reviews.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_orders():
    data = apps.get_model("orders", "Order")
    field_names = [
        "id",
        "order_number",
        "ordering_date",
        "status",
        "payment_method",
        "is_paid",
        "comment",
        "delivery_method",
        "package",
        "address_id",
        "delivery_point_id",
        "user_id",
        "add_address",
        "total_price",
        "user_data",
    ]
    with open(
        os.path.join(DATA_DIR, "orders.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_shopping_cart():
    data = apps.get_model("orders", "ShoppingCart")
    field_names = ["id", "created", "product_id", "user_id"]
    with open(
        os.path.join(DATA_DIR, "shopping_cart.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_order_products():
    data = apps.get_model("orders", "OrderProduct")
    field_names = ["id", "quantity", "order_id", "product_id"]
    with open(
        os.path.join(DATA_DIR, "order_products.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_sessions():
    data = apps.get_model("sessions", "Session")
    field_names = ["_state", "session_key", "session_data", "expire_date"]
    with open(
        os.path.join(DATA_DIR, "sessions.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for obj in data.objects.all():
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)


def export_recipes():
    data = apps.get_model("recipes", "Recipe")
    field_names = [
        "id",
        "pub_date",
        "author_id",
        "name",
        "image",
        "text",
        "cooking_time",
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
    field_names = ["id", "recipe_id", "ingredient_id", "amount"]
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
        export_products()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Product прошёл успешно.")
        )
        export_products_components()
        self.stdout.write(
            self.style.SUCCESS(
                "Экспорт данных поля components модели Product прошёл успешно."
            )
        )
        export_products_tags()
        self.stdout.write(
            self.style.SUCCESS(
                "Экспорт данных поля tags модели Product прошёл успешно."
            )
        )
        export_categories()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Category прошёл успешно.")
        )
        export_subcategories()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Subcategory прошёл успешно.")
        )
        export_components()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Component прошёл успешно.")
        )
        export_tags()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Tag прошёл успешно.")
        )
        export_producers()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Producer прошёл успешно.")
        )
        export_promotions()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Promotion прошёл успешно.")
        )
        export_products_promotions()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели ProductPromoton прошёл успешно.")
        )
        export_users()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели User прошёл успешно.")
        )
        export_delivery_points()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Delivery прошёл успешно.")
        )
        export_favorites()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели FavoriteProduct прошёл успешно.")
        )
        export_user_address()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Address прошёл успешно.")
        )
        export_tokens()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Token прошёл успешно.")
        )
        export_reviews()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Review прошёл успешно.")
        )
        export_orders()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Order прошёл успешно.")
        )
        export_order_products()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели OrderProduct прошёл успешно.")
        )
        export_sessions()
        self.stdout.write(
            self.style.SUCCESS("Экспорт данных модели Session прошёл успешно.")
        )
        export_recipes()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Recipe прошёл успешно.")
        )
        export_products_in_recipe()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели ProductsInRecipe прошёл успешно.")
        )
