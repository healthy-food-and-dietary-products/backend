from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_cleanup import cleanup
from phonenumber_field.modelfields import PhoneNumberField

from users import utils


@cleanup.select
class User(AbstractUser):
    """Extending the Built-in Model User."""

    def user_directory_path(self, filename):
        """Constructs the path which the users photo will be saved."""
        return f"images/{self.username}"

    username = models.CharField(
        "Username",
        unique=True,
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        help_text="150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )
    email = models.EmailField("E-mail address", unique=True, max_length=254)
    city = models.CharField(
        "City", choices=utils.city_choices, max_length=50, default="Moscow"
    )
    birth_date = models.DateField("Birth_date", blank=True, null=True)
    phone_number = PhoneNumberField("Phone_number", blank=True)
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
        """Checks the user's birth date."""
        super().clean_fields(exclude=exclude)
        now = timezone.now()
        if self.birth_date:
            if (
                self.birth_date.year > now.year
                or (now.year - self.birth_date.year) > 120
            ):
                raise ValidationError("Указана неверная дата рождения.")


class Address(models.Model):
    """Describes address of user."""

    address = models.TextField("Address")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="User",
    )
    priority_address = models.BooleanField("Priority", default=False)

    def __str__(self):
        return f"{self.address}"

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "address"], name="unique_user_address"
            )
        ]
