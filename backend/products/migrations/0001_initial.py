# Generated by Django 4.2.7 on 2023-11-08 07:05

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import products.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, unique=True, verbose_name="Name"),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True, max_length=100, unique=True, verbose_name="Slug"
                    ),
                ),
            ],
            options={
                "verbose_name": "Category",
                "verbose_name_plural": "Categories",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Component",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Component name",
                        max_length=100,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Component slug",
                        max_length=100,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
            ],
            options={
                "verbose_name": "Component",
                "verbose_name_plural": "Components",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Producer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Producer name",
                        max_length=100,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Producer slug",
                        max_length=100,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "producer_type",
                    models.CharField(
                        choices=[
                            ("company", "Юридическое лицо"),
                            ("entrepreneur", "Индивидуальный предприниматель"),
                        ],
                        default="company",
                        max_length=12,
                        verbose_name="Producer type",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Brief information about the company or entrepreneur",
                        verbose_name="Description",
                    ),
                ),
                (
                    "address",
                    models.TextField(
                        help_text="Legal address of the producers",
                        verbose_name="Address",
                    ),
                ),
            ],
            options={
                "verbose_name": "Producer",
                "verbose_name_plural": "Producers",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Product name",
                        max_length=100,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Product description",
                        verbose_name="Description",
                    ),
                ),
                (
                    "creation_time",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date of inclusion of the product in the database",
                        verbose_name="Creation time",
                    ),
                ),
                (
                    "discontinued",
                    models.BooleanField(
                        default=False,
                        help_text="Is this product discontinued from sale",
                        verbose_name="Discontinued",
                    ),
                ),
                (
                    "measure_unit",
                    models.CharField(
                        choices=[
                            ("grams", "г."),
                            ("milliliters", "мл."),
                            ("items", "шт."),
                        ],
                        default="items",
                        max_length=11,
                        verbose_name="Measure unit",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text="Number of grams, milliliters or items",
                        verbose_name="Amount",
                    ),
                ),
                (
                    "price",
                    models.FloatField(
                        help_text="Price per one product unit",
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Price",
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        upload_to=products.models.Product.product_directory_path,
                        verbose_name="Photo",
                    ),
                ),
                (
                    "kcal",
                    models.PositiveSmallIntegerField(
                        help_text="Number of kcal per 100 g of product",
                        verbose_name="Kcal",
                    ),
                ),
                (
                    "proteins",
                    models.PositiveSmallIntegerField(
                        help_text="Number of proteins per 100 g of product",
                        verbose_name="Proteins",
                    ),
                ),
                (
                    "fats",
                    models.PositiveSmallIntegerField(
                        help_text="Number of fats per 100 g of product",
                        verbose_name="Fats",
                    ),
                ),
                (
                    "carbohydrates",
                    models.PositiveSmallIntegerField(
                        help_text="Number of carbohydrates per 100 g of product",
                        verbose_name="Carbohydrates",
                    ),
                ),
                (
                    "views_number",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of product page views",
                        verbose_name="Views number",
                    ),
                ),
                (
                    "orders_number",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of orders for this product",
                        verbose_name="Orders number",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="products.category",
                        verbose_name="Category",
                    ),
                ),
                (
                    "components",
                    models.ManyToManyField(
                        related_name="products",
                        to="products.component",
                        verbose_name="Components that the product consists of",
                    ),
                ),
                (
                    "producer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="products.producer",
                        verbose_name="Producer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Promotion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "promotion_type",
                    models.CharField(
                        choices=[
                            ("simple", "Простая скидка"),
                            ("birthday", "Скидка именинникам"),
                            ("loyalty_card", "Скидка по карте покупателя"),
                            (
                                "expired_soon",
                                "Скидка на товары с истекающим сроком годности",
                            ),
                            ("present", "Товар в подарок"),
                            ("two_for_one", "Два по цене одного"),
                            ("multiple_items", "Скидка при покупке нескольких штук"),
                        ],
                        default="simple",
                        max_length=14,
                        verbose_name="Promotion type",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Promotion name",
                        max_length=100,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "discount",
                    models.PositiveSmallIntegerField(
                        default=0,
                        error_messages={"invalid": "Допустимы числа от 0 до 100"},
                        help_text="Percentage of a product price",
                        validators=[django.core.validators.MaxValueValidator(100)],
                        verbose_name="Discount",
                    ),
                ),
                (
                    "conditions",
                    models.TextField(
                        blank=True,
                        help_text="Conditions of the promotion",
                        verbose_name="Conditions",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Is this promotion valid now",
                        verbose_name="Active or not",
                    ),
                ),
                (
                    "is_constant",
                    models.BooleanField(
                        default=False,
                        help_text="Does this promotion have a time limits",
                        verbose_name="Constant or not",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Promotion start time"
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Promotion end time"
                    ),
                ),
            ],
            options={
                "verbose_name": "Promotion",
                "verbose_name_plural": "Promotions",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Tag name",
                        max_length=100,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Tag slug",
                        max_length=100,
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Subcategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, unique=True, verbose_name="Name"),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True, max_length=100, unique=True, verbose_name="Slug"
                    ),
                ),
                (
                    "parent_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subcategories",
                        to="products.category",
                        verbose_name="Category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Subcategory",
                "verbose_name_plural": "Subcategories",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="ProductPromotion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
                (
                    "promotion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.promotion",
                    ),
                ),
            ],
            options={
                "verbose_name": "ProductPromotion",
                "verbose_name_plural": "ProductPromotions",
                "ordering": ["id"],
            },
        ),
        migrations.AddField(
            model_name="product",
            name="promotions",
            field=models.ManyToManyField(
                blank=True,
                related_name="products",
                through="products.ProductPromotion",
                to="products.promotion",
                verbose_name="Promotions",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="subcategory",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="products.subcategory",
                verbose_name="Subcategory",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="products",
                to="products.tag",
                verbose_name="Tags",
            ),
        ),
        migrations.CreateModel(
            name="FavoriteProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="products.product",
                        verbose_name="Product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Favorite Product",
                "verbose_name_plural": "Favorite Products",
                "ordering": ["id"],
            },
        ),
    ]
