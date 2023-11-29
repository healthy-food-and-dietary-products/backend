# Generated by Django 4.2.7 on 2023-11-29 11:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0005_orderproduct_remove_order_shopping_cart_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="address_anonymous",
            field=models.CharField(
                blank=True,
                max_length=450,
                null=True,
                verbose_name="Anonimus user's address",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_price",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Order's total_price"
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="user_data",
            field=models.CharField(
                blank=True,
                max_length=450,
                null=True,
                verbose_name="Anonimus user's data",
            ),
        ),
    ]