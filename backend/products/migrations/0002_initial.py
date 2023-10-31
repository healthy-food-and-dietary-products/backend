# Generated by Django 4.2.6 on 2023-10-27 06:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="favoriteproduct",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AddConstraint(
            model_name="productpromotion",
            constraint=models.UniqueConstraint(
                fields=("product", "promotion"), name="unique_product_promotion"
            ),
        ),
        migrations.AddConstraint(
            model_name="favoriteproduct",
            constraint=models.UniqueConstraint(
                fields=("user", "product"), name="unique_favorite_user"
            ),
        ),
    ]
