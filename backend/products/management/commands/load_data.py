import os
from csv import DictReader

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.utils import timezone
from rest_framework.authtoken.models import Token

from good_food.settings import BASE_DIR
from orders.models import Delivery
from products.models import (
    Category,
    Component,
    FavoriteProduct,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)
from reviews.models import Review
from users.models import Address, User

DATA_DIR = os.path.join(BASE_DIR, "data")


def read_users():
    with open(os.path.join(DATA_DIR, "users.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            user = User(
                id=row["id"],
                password=row["password"],
                last_login=None if row["last_login"] == "" else row["last_login"],
                is_superuser=row["is_superuser"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                is_staff=row["is_staff"],
                is_active=row["is_active"],
                date_joined=row["date_joined"],
                username=row["username"],
                email=row["email"],
                city=row["city"],
                birth_date=None if row["birth_date"] == "" else row["birth_date"],
                phone_number=row["phone_number"],
                photo=row["photo"],
            )
            user.save()


def read_category():
    with open(os.path.join(DATA_DIR, "category.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            category = Category(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
                image=row["image"],
            )
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
                image=row["image"],
            )
            subcategory.save()


def read_tags():
    with open(os.path.join(DATA_DIR, "tags.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            tag = Tag(
                id=row["id"], name=row["name"], slug=row["slug"], image=row["image"]
            )
            tag.save()


def read_producer():
    with open(os.path.join(DATA_DIR, "producer.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            producer = Producer(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
                producer_type=row["producer_type"],
                description=row["description"],
                address=row["address"],
                image=row["image"],
            )
            producer.save()


def read_components():
    with open(os.path.join(DATA_DIR, "components.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            component = Component(id=row["id"], name=row["name"], slug=row["slug"])
            component.save()


def read_promotions():
    with open(os.path.join(DATA_DIR, "promotions.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            promotion = Promotion(
                id=row["id"],
                promotion_type=row["promotion_type"],
                name=row["name"],
                slug=row["slug"],
                discount=row["discount"],
                conditions=row["conditions"],
                is_active=row["is_active"],
                is_constant=row["is_constant"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                image=row["image"],
            )
            promotion.save()


def read_products():
    with open(os.path.join(DATA_DIR, "products.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            if row.get("creation_time"):
                creation_time = row["creation_time"]
            else:
                creation_time = timezone.now()
            product = Product(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                creation_time=creation_time,
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


def read_favorites():
    with open(os.path.join(DATA_DIR, "favorites.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            favorite_product = FavoriteProduct(
                id=row["id"],
                product_id=row["product_id"],
                user_id=row["user_id"],
            )
            favorite_product.save()


def read_delivery_points():
    with open(
        os.path.join(DATA_DIR, "delivery_points.csv"), "r", encoding="utf-8"
    ) as f:
        reader = DictReader(f)
        for row in reader:
            delivery_point = Delivery(
                id=row["id"],
                delivery_point=row["delivery_point"],
            )
            delivery_point.save()


def read_user_addresses():
    with open(os.path.join(DATA_DIR, "user_addresses.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            address = Address(
                id=row["id"],
                address=row["address"],
                priority_address=row["priority_address"],
                user_id=row["user_id"],
            )
            address.save()


def read_tokens():
    with open(os.path.join(DATA_DIR, "tokens.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            token = Token(
                key=row["key"], created=row["created"], user_id=row["user_id"]
            )
            token.save()


def read_reviews():
    with open(os.path.join(DATA_DIR, "reviews.csv"), "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            review = Review(
                id=row["id"],
                text=row["text"],
                score=row["score"],
                pub_date=row["pub_date"],
                author_id=row["author_id"],
                product_id=row["product_id"],
            )
            review.save()


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
        read_favorites()
        self.stdout.write("Данные из файла favorites.csv загружены")
        read_delivery_points()
        self.stdout.write("Данные из файла delivery_points.csv загружены")
        read_user_addresses()
        self.stdout.write("Данные из файла user_addresses.csv загружены")
        read_tokens()
        self.stdout.write("Данные из файла tokens.csv загружены")
        read_reviews()
        self.stdout.write("Данные из файла reviews.csv загружены")

        model_list = [
            Delivery,
            Category,
            Component,
            FavoriteProduct,
            Producer,
            Product,
            Promotion,
            Subcategory,
            Tag,
            Review,
            Address,
            User,
            Token,
        ]
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), model_list)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
