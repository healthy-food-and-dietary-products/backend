# Generated by Django 4.2.6 on 2023-10-27 06:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
        ("orders", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Покупатель",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.address",
                verbose_name="Адрес покупателя",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="shopping_cart",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="orders.shoppingcart",
            ),
        ),
        migrations.AddConstraint(
            model_name="shoppingcartproduct",
            constraint=models.UniqueConstraint(
                fields=("shopping_cart", "product"),
                name="unique_shopping_cart_products",
            ),
        ),
    ]