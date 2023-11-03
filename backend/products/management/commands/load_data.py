import os
from csv import DictReader

from django.core.management.base import BaseCommand

from good_food.settings import BASE_DIR
from products.models import (
    Category,
    Component,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)
from users.models import User
from orders.models import Delivery

DATA_DIR = os.path.join(BASE_DIR, "data")


def read_users():
    with open(os.path.join(DATA_DIR, "users.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            user = User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                password=row["password"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                city="Moscow",
            )
            user.save()


def read_category():
    with open(os.path.join(DATA_DIR, "category.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            category = Category(id=row["id"], name=row["name"], slug=row["slug"])
            category.save()


def read_subcategory():
    with open(os.path.join(DATA_DIR, "subcategory.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            subcategory = Subcategory(
                id=row["id"],
                parent_category_id=row["parent_category_id"],
                name=row["name"],
                slug=row["slug"],
            )
            subcategory.save()


def read_tags():
    with open(os.path.join(DATA_DIR, "tags.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            tag = Tag(id=row["id"], name=row["name"], slug=row["slug"])
            tag.save()


def read_producer():
    with open(os.path.join(DATA_DIR, "producer.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            producer = Producer(
                id=row["id"],
                name=row["name"],
                producer_type=row["producer_type"],
                description=row["description"],
                address=row["address"],
            )
            producer.save()


def read_components():
    with open(os.path.join(DATA_DIR, "components.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            component = Component(id=row["id"], name=row["name"])
            component.save()


def read_promotions():
    with open(os.path.join(DATA_DIR, "promotions.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            promotion = Promotion(
                id=row["id"],
                promotion_type=row["promotion_type"],
                name=row["name"],
                discount=row["discount"],
            )
            promotion.save()


def read_products():
    with open(os.path.join(DATA_DIR, "products.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            product = Product(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                category_id=row["category_id"],
                subcategory_id=row["subcategory_id"],
                producer_id=row["producer_id"],
                measure_unit=row["measure_unit"],
                amount=row["amount"],
                price=row["price"],
                photo=row["photo"],
                kcal=row["kcal"],
                proteins=row["proteins"],
                fats=row["fats"],
                carbohydrates=row["carbohydrates"],
            )
            product.save()


def read_products_components():
    with open(
        os.path.join(DATA_DIR, "products_components.csv"), "r", encoding="utf-8"
    ) as f:
        reader = DictReader(f)
        for row in reader:
            product = Product.objects.get(id=row["product_id"])
            component = Component.objects.get(id=row["component_id"])
            product.components.add(component)


def read_products_tags():
    with open(os.path.join(DATA_DIR, "products_tags.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            product = Product.objects.get(id=row["product_id"])
            tag = Tag.objects.get(id=row["tag_id"])
            product.tags.add(tag)


def read_products_promotions():
    with open(
        os.path.join(DATA_DIR, "products_promotions.csv"), "r", encoding="utf-8"
    ) as f:
        reader = DictReader(f)
        for row in reader:
            product = Product.objects.get(id=row["product_id"])
            promotion = Promotion.objects.get(id=row["promotion_id"])
            product.promotions.add(promotion)


def read_delivery_points():
    with open(os.path.join(DATA_DIR, "delivery_points.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            delivery_point = Delivery(
                id=row["id"],
                delivery_point=row["delivery_point"],
            )
            delivery_point.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        read_users()
        self.stdout.write("Данные из файла users.csv загружены")
        read_category()
        self.stdout.write("Данные из файла category.csv загружены")
        read_subcategory()
        self.stdout.write("Данные из файла subcategory.csv загружены")
        read_tags()
        self.stdout.write("Данные из файла tags.csv загружены")
        read_producer()
        self.stdout.write("Данные из файла producer.csv загружены")
        read_components()
        self.stdout.write("Данные из файла components.csv загружены")
        read_promotions()
        self.stdout.write("Данные из файла promotions.csv загружены")
        read_products()
        self.stdout.write("Данные из файла products.csv загружены")
        read_products_components()
        self.stdout.write("Данные из файла products_components.csv загружены")
        read_products_tags()
        self.stdout.write("Данные из файла products_tags.csv загружены")
        read_products_promotions()
        self.stdout.write("Данные из файла products_promotions.csv загружены")
        read_delivery_points()
        self.stdout.write("Данные из файла delivery_points.csv загружены")
