import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from products.models import Category, Product
from users.models import User


def read_users():
    with open(os.path.join(settings.BASE_DIR, 'data', 'users.csv'),
              'r', encoding='utf-8'
            ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            User.objects.get_or_create(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3],
                first_name=row[4],
                last_name=row[5],
                # role=row[6]

            )
    print('Данные из файла users.csv загружены')


def read_category():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'data', 'category.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Category.objects.get_or_create(
                id=row[0],
                name=row[1],
                slug=row[2],
            )
    print('Данные из файла category.csv загружены')


def read_products():
    with open(
            os.path.join(
                settings.BASE_DIR,
                'data', 'products.csv',
            ),
            'r', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'id':
                continue
            Product.objects.get_or_create(
                id=row[0],
                name=row[1],
                measure_unit=row[2],
                amount=row[3],
                description=row[4],
                image=row[5],
                producer=row[6],
                category=row[7],
                price=row[8]
            )
    print('Данные из файла products.csv загружены')


class Command(BaseCommand):

    def handle(self, *args, **options):
        read_users()
        read_category()
        read_products()



