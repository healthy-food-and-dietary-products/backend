# Generated by Django 4.2.7 on 2023-11-06 18:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0008_order_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("Payment at the point of delivery", "Оплата в пункте самовывоза"),
                    ("In getting by cash", "Оплата наличными курьеру"),
                ],
                default="Картой на сайте",
                max_length=50,
                verbose_name="Payment Method",
            ),
        ),
    ]
