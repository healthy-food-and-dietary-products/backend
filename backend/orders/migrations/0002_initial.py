# Generated by Django 4.2.6 on 2023-10-26 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("products", "0001_initial"),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcartproduct",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="products.product",
                verbose_name="Продукт в корзине",
            ),
        ),
        migrations.AddField(
            model_name="shoppingcartproduct",
            name="shopping_cart",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_carts",
                to="orders.shoppingcart",
                verbose_name="Корзина",
            ),
        ),
        migrations.AddField(
            model_name="shoppingcart",
            name="products",
            field=models.ManyToManyField(
                through="orders.ShoppingCartProduct",
                to="products.product",
                verbose_name="Продукты в корзине",
            ),
        ),
    ]
