from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    country = models.CharField(
        "Country",
        null=False,
        blank=False,
        max_length=100,
    )
    city = models.CharField(
        "City",
        null=False,
        blank=False,
        max_length=100,
    )
    street = models.CharField(
        "Street",
        null=False,
        blank=False,
        max_length=100,
    )
    house = models.IntegerField(
        "House_number",
        null=False,
        blank=False,
    )
    building = models.IntegerField(
        "Buiding_number",
        null=True,
        blank=True,
    )
    apartment = models.IntegerField(
        "Apartment_number",
        null=False,
        blank=False,
    )

    def __str__(self):
        return (
            f"{self.country}, {self.city}, {self.street}, "
            f"{self.house}{self.building}, {self.apartment}"
        )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        constraints = [
            models.UniqueConstraint(
                fields=["city", "street", "house", "building", "apartment"],
                name="unique address",
            )
        ]


class User(AbstractUser):
    """
    Расширение встроенной модели User."""

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

    username: str = models.CharField(
        "Username",
        unique=True,
        max_length=150,
    )
    email: str = models.EmailField(
        "E-mail address",
        unique=True,
        blank=False,
        max_length=254,
    )
    role: str = models.CharField(
        max_length=9,
        choices=CHOISES,
        default="user",
    )
    city: str = models.CharField(
        "City",
        max_length=30,
        blank=True,
    )
    birth_date = models.DateField(
        "Birth_date",
        blank=True,
        null=True,
    )
    address = models.ManyToManyField(
        Address,
        related_name="users",
        verbose_name="Addresses",
    )
    address_quantity = models.IntegerField(
        "number_of_cities",
        default=0,
        validators=[MaxValueValidator(5)],
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
        if self.birth_date > now or (now.year - self.birth_date.year) > 120:
            raise ValidationError("Введен неверный возраст.")

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_user(self):
        return self.role == User.USER
