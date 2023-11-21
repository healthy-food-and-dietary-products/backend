# Generated by Django 4.2.7 on 2023-11-21 12:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0002_initial"),
        ("orders", "0004_alter_order_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderProduct",
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
                    "quantity",
                    models.PositiveIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, "Разрешены значения от 1 до 10000"
                            ),
                            django.core.validators.MaxValueValidator(
                                10000, "Разрешены значения от 1 до 10000"
                            ),
                        ],
                        verbose_name="Количество",
                    ),
                ),
            ],
            options={
                "verbose_name": "Продукты в заказе",
                "verbose_name_plural": "Продукты  в заказе",
            },
        ),
        migrations.RemoveField(
            model_name="order",
            name="shopping_cart",
        ),
        migrations.RemoveField(
            model_name="shoppingcart",
            name="products",
        ),
        migrations.RemoveField(
            model_name="shoppingcart",
            name="status",
        ),
        migrations.RemoveField(
            model_name="shoppingcart",
            name="total_price",
        ),
        migrations.AddField(
            model_name="shoppingcart",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.product",
                verbose_name="Продукт в корзине",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Покупатель",
            ),
        ),
        migrations.AlterField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_carts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Покупатель",
            ),
        ),
        migrations.DeleteModel(
            name="ShoppingCartProduct",
        ),
        migrations.AddField(
            model_name="orderproduct",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="orders.order",
                verbose_name="Заказ",
            ),
        ),
        migrations.AddField(
            model_name="orderproduct",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="products.product",
                verbose_name="Продукт в корзине",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                through="orders.OrderProduct",
                to="products.product",
                verbose_name="Продукты в заказе",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderproduct",
            constraint=models.UniqueConstraint(
                fields=("order", "product"), name="unique_order_products"
            ),
        ),
    ]