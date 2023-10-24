from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_cleanup import cleanup
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    """Describes address of user."""

    country = models.CharField(
        "Country",
        max_length=100,
    )
    region = models.CharField(
        "Region",
        max_length=200,
    )
    city_type = models.CharField(
        "City_type",
        max_length=100,
    )
    city = models.CharField(
        "City",
        max_length=100,
    )
    microdistrict = models.CharField(
        "Microdistrict",
        null=True,
        blank=True,
        max_length=150,
    )
    street_type = models.CharField(
        "Street_type",
        max_length=100,
        null=True,
        blank=True,
    )
    street = models.CharField(
        "Street",
        max_length=100,
        null=True,
        blank=True,
    )
    house = models.CharField(
        "House_number",
        max_length=40,
    )
    apartment = models.IntegerField(
        "Apartment_number",
        null=True,
        blank=True,
    )
    postal_code = models.CharField(
        "Postal_code",
        max_length=6,
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.country}, {self.city}, {self.street}, "
            f"{self.house}, {self.apartment}"
        )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        constraints = [
            models.UniqueConstraint(
                fields=["city", "street", "house", "apartment"],
                name="unique address",
            )
        ]


@cleanup.select
class User(AbstractUser):
    """Extending the Built-in Model User."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    CHOISES = [
        (USER, "Аутентифицированный пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Администратор"),
    ]

    def user_directory_path(self, filename):
        """Constructs the path which the users photo will be saved."""
        return f"images/{self.username}"

    username = models.CharField(
        "Username",
        unique=True,
        max_length=150,
    )
    email = models.EmailField(
        "E-mail address",
        unique=True,
        max_length=254,
    )
    role = models.CharField(
        max_length=9,
        choices=CHOISES,
        default="user",
    )
    city = models.CharField(
        "City",
        max_length=50,
        blank=True,
    )
    birth_date = models.DateField(
        "Birth_date",
        blank=True,
        null=True,
    )
    address = models.ManyToManyField(
        Address,
        through="UserAddress",
        blank=True,
        related_name="users",
        verbose_name="Addresses",
    )
    address_quantity = models.IntegerField(
        "number_of_adresses",
        default=0,
        validators=[validators.MaxValueValidator(5)],
    )
    phone_number = PhoneNumberField(
        "Phone_number",
        blank=True,
    )
    photo = models.ImageField(
        "Photo",
        upload_to=user_directory_path,
        blank=True,
        default="default.jpg",
    )

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.username

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)

        now = timezone.now()
        if self.birth_date:
            if (
                self.birth_date.year > now.year
                or (now.year - self.birth_date.year) > 120
            ):
                raise ValidationError("Указана неверная дата рождения.")

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_user(self):
        return self.role == User.USER


class UserAddress(models.Model):
    """Decribes User-Address relation."""

    user = models.ForeignKey(
        User, related_name="user_addresses", on_delete=models.CASCADE
    )
    address = models.ForeignKey(
        Address, related_name="user_addresses", on_delete=models.CASCADE
    )
    priority_address = models.BooleanField(default=True)
