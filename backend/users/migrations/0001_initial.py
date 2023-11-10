# Generated by Django 4.2.7 on 2023-11-09 07:43

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import users.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="Username"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="E-mail address"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("user", "Аутентифицированный пользователь"),
                            ("moderator", "Модератор"),
                            ("admin", "Администратор"),
                        ],
                        default="user",
                        max_length=9,
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        choices=[("Moscow", "Москва")],
                        default="Moscow",
                        max_length=50,
                        verbose_name="City",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(blank=True, null=True, verbose_name="Birth_date"),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        max_length=128,
                        region=None,
                        verbose_name="Phone_number",
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        default="default.jpg",
                        upload_to=users.models.User.user_directory_path,
                        verbose_name="Photo",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Address",
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
                ("address", models.TextField(verbose_name="Address")),
                (
                    "priority_address",
                    models.BooleanField(default=False, verbose_name="Priority"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Address",
                "verbose_name_plural": "Addresses",
            },
        ),
        migrations.AddConstraint(
            model_name="address",
            constraint=models.UniqueConstraint(
                fields=("user", "address"), name="unique_user_address"
            ),
        ),
    ]
