from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_cleanup import cleanup
from phonenumber_field.modelfields import PhoneNumberField

from users import utils


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

    username = models.CharField("Username", unique=True, max_length=150)
    email = models.EmailField("E-mail address", unique=True, max_length=254)
    role = models.CharField(max_length=9, choices=CHOISES, default="user")
    city = models.CharField(
        "City", choices=utils.city_choices, max_length=50, default="Moscow"
    )
    birth_date = models.DateField("Birth_date", blank=True, null=True)
    # address = models.ForeignKey(
    #     Address,
    #     blank=True,
    #     null=True,
    #     on_delete=models.SET_NULL,
    #     related_name="users",
    #     verbose_name="Addresses",
    # )
    phone_number = PhoneNumberField("Phone_number", blank=True)
    photo = models.ImageField(
        "Photo", upload_to=user_directory_path, blank=True, default="default.jpg",
    )

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.username

    def clean_fields(self, exclude=None):
        """Checks the user's birth date."""
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


class Address(models.Model):
    """Describes address of user."""

    address = models.TextField("Address", unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Address",
    )
    priority_address = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address}"

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    # def clean_fields(self, exclude=None):
    #     """Checks that the user has only one priority address."""
    #     super().clean_fields(exclude=exclude)
    #     priority_count = 1 if self.priority_address else 0
    #     for address in self.user.user_addresses.all():
    #         if address.priority_address:
    #             priority_count += 1
    #     if priority_count > 1:
    #         raise ValidationError(
    #             "У пользователя может быть только один приоритетный адрес."
    #         )
    # this func don't work. Fix it.
