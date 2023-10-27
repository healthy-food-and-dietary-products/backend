import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from products.models import Category, Component, Producer, Product, Subcategory, Tag
from users.models import User


def read_users():
    with open(
        os.path.join(settings.BASE_DIR, "data", "users.csv"), "r", encoding="utf-8"
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            User.objects.get_or_create(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3],
                first_name=row[4],
                last_name=row[5],
            )
    print("Данные из файла users.csv загружены")


def read_category():
    with open(
        os.path.join(settings.BASE_DIR, "data", "category.csv",), "r", encoding="utf-8",
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            Category.objects.get_or_create(
                id=row[0], name=row[1], slug=row[2],
            )
    print("Данные из файла category.csv загружены")


def read_subcategory():
    with open(
        os.path.join(settings.BASE_DIR, "data", "subcategory.csv",),
        "r",
        encoding="utf-8",
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            Subcategory.objects.get_or_create(
                id=row[0], parent_category_id=row[1], name=row[2], slug=row[3]
            )
    print("Данные из файла subcategory.csv загружены")


def read_tags():
    with open(
        os.path.join(settings.BASE_DIR, "data", "tags.csv",), "r", encoding="utf-8",
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            Tag.objects.get_or_create(
                id=row[0], name=row[1], slug=row[2],
            )
    print("Данные из файла tags.csv загружены")


def read_producer():
    with open(
        os.path.join(settings.BASE_DIR, "data", "producer.csv",), "r", encoding="utf-8",
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            Producer.objects.get_or_create(
                id=row[0],
                name=row[1],
                producer_type=row[2],
                description=row[3],
                address=row[4],
            )
    print("Данные из файла producer.csv загружены")


def read_components():
    with open(
        os.path.join(settings.BASE_DIR, "data", "components.csv",),
        "r",
        encoding="utf-8",
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            Component.objects.get_or_create(
                id=row[0], name=row[1],
            )
    print("Данные из файла components.csv загружены")


def read_products():
    with open(
        os.path.join(settings.BASE_DIR, "data", "products.csv",), "r", encoding="utf-8",
    ) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if row[0] == "id":
                continue
            Product.objects.get_or_create(
                id=row[0],
                name=row[1],
                description=row[2],
                categorу_id=row[3],
                subcategory_id=row[4],
                tags=row[5],
                discontinued=row[6],
                producer_id=row[7],
                measure_unit=row[8],
                amount=row[9],
                price=row[10],
                photo=row[11],
                components=row[12],
                kcal=row[13],
                proteins=row[14],
                fats=row[15],
                carbohydrates=row[16],
            )
    print("Данные из файла products.csv загружены")


class Command(BaseCommand):
    def handle(self, *args, **options):
        read_users()
        read_category()
        read_tags()
        read_producer()
        read_components()
        read_subcategory()
        read_products()
