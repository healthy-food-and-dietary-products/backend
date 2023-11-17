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
            id += 1
            components = product.components.all()
            for component in components:
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
            id += 1
            tags = product.tags.all()
            for tag in tags:
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
    field_names = ["id", "name", "slug", "parent_category_id"]
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
        os.path.join(DATA_DIR, "user_address.csv"),
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
        os.path.join(DATA_DIR, "favorite_products.csv"),
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
        "shopping_cart_id",
        "user_id",
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
    field_names = [
        "id",
        "status",
        "total_price",
        "created",
        "user_id"
    ]
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


def export_shopping_cart_products():
    data = apps.get_model("orders", "ShoppingCartProduct")
    field_names = [
        "id",
        "quantity",
        "product_id",
        "shopping_cart_id"
    ]
    with open(
        os.path.join(DATA_DIR, "shopping_cart_products.csv"),
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
            self.style.SUCCESS("Экспорт даных модели Product прошёл успешно!")
        )
        export_products_components()
        self.stdout.write(
            self.style.SUCCESS(
                "Экспорт даных поля components модели Product прошёл успешно!"
            )
        )
        export_products_tags()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных поля tags модели Product прошёл успешно!")
        )
        export_categories()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Category прошёл успешно!")
        )
        export_subcategories()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Subcategory прошёл успешно!")
        )
        export_components()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Component прошёл успешно!")
        )
        export_tags()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Tag прошёл успешно!")
        )
        export_producers()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Producer прошёл успешно!")
        )
        export_promotions()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Promotion прошёл успешно!")
        )
        export_products_promotions()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели ProductPromoton прошёл успешно!")
        )
        export_users()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели User прошёл успешно!")
        )
        export_delivery_points()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Delivery прошёл успешно!")
        )
        export_favorites()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели FavoriteProduct прошёл успешно!")
        )
        export_user_address()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Address прошёл успешно!")
        )
        export_orders()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели Order прошёл успешно!")
        )
        export_shopping_cart()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели ShoppingCart прошёл успешно!")
        )
        export_shopping_cart_products()
        self.stdout.write(
            self.style.SUCCESS("Экспорт даных модели ShoppingCartProduct прошёл успешно!")
        )
