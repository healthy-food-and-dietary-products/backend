# Generated by Django 4.2.7 on 2023-11-05 12:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0006_order_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="user",
        ),
    ]
