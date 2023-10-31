# Generated by Django 4.2.6 on 2023-10-31 12:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="producer",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Producer slug",
                max_length=100,
                unique=True,
                verbose_name="Slug",
            ),
        ),
    ]
