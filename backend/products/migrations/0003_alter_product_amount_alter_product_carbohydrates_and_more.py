# Generated by Django 4.2.7 on 2023-11-27 10:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="amount",
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text="Number of grams, milliliters or items",
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Amount",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="carbohydrates",
            field=models.FloatField(
                default=0,
                help_text="Number of carbohydrates per 100 g of product",
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Carbohydrates",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="fats",
            field=models.FloatField(
                default=0,
                help_text="Number of fats per 100 g of product",
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Fats",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="kcal",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text="Number of kcal per 100 g of product",
                verbose_name="Kcal",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="proteins",
            field=models.FloatField(
                default=0,
                help_text="Number of proteins per 100 g of product",
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Proteins",
            ),
        ),
    ]
