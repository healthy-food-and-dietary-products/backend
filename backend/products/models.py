from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import CategoryModel


class Category(CategoryModel):
    """Describes product categories."""

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]


class Subcategory(CategoryModel):
    """Describes product subcategories."""

    parent_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Category",
    )

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ["name"]


class Component(models.Model):
    """Describes what the product consists of."""

    name = models.CharField(
        "Name", max_length=100, unique=True, help_text="Component name"
    )

    class Meta:
        verbose_name = "Component"
        verbose_name_plural = "Components"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Describes product tags."""

    name = models.CharField("Name", max_length=100, unique=True, help_text="Tag name")
    slug = models.SlugField(
        "Slug", max_length=100, unique=True, blank=True, help_text="Tag slug"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Makes slug from a tag name."""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)[:50]
        super().save(*args, **kwargs)


class Producer(models.Model):
    """Describes product producers."""

    COMPANY = "company"
    ENTREPRENEUR = "entrepreneur"

    CHOISES = [
        (COMPANY, "Юридическое лицо"),
        (ENTREPRENEUR, "Индивидуальный предприниматель"),
    ]

    name = models.CharField(
        "Name", max_length=100, unique=True, help_text="Producer name"
    )
    producer_type = models.CharField(
        "Producer type", max_length=12, choices=CHOISES, default=COMPANY
    )
    description = models.TextField(
        "Description",
        blank=True,
        help_text="Brief information about the company or entrepreneur",
    )
    # TODO: think, do we need to connect the address field to the Address model (users)
    address = models.TextField("Address", help_text="Legal address of the producers")

    class Meta:
        verbose_name = "Producer"
        verbose_name_plural = "Producers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Promotion(models.Model):
    """Describes promotions applied to products."""

    SIMPLE = "simple"
    BIRTHDAY = "birthday"
    LOYALTY_CARD = "loyalty_card"
    EXPIRED_SOON = "expired_soon"
    PRESENT = "present"
    TWO_FOR_ONE = "two_for_one"
    MULTIPLE_ITEMS = "multiple_items"

    CHOISES = [
        (SIMPLE, "Простая скидка"),
        (BIRTHDAY, "Скидка именинникам"),
        (LOYALTY_CARD, "Скидка по карте покупателя"),
        (EXPIRED_SOON, "Скидка на товары с истекающим сроком годности"),
        (PRESENT, "Товар в подарок"),
        (TWO_FOR_ONE, "Два по цене одного"),
        (MULTIPLE_ITEMS, "Скидка при покупке нескольких штук"),
    ]

    promotion_type = models.CharField(
        "Promotion type", max_length=14, choices=CHOISES, default=SIMPLE
    )
    name = models.CharField(
        "Name", max_length=100, unique=True, help_text="Promotion name"
    )
    # TODO: add validation error for discount (django.core.exceptions.ValidationError)
    discount = models.PositiveSmallIntegerField(
        "Discount",
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Percentage of a product price",
    )
    conditions = models.TextField(
        "Conditions", blank=True, help_text="Conditions of the promotion"
    )
    is_active = models.BooleanField(
        "Active or not", default=True, help_text="Is this promotion valid now"
    )
    is_constant = models.BooleanField(
        "Constant or not",
        default=False,
        help_text="Does this promotion have a time limits",
    )
    start_time = models.DateTimeField("Promotion start time", blank=True)
    end_time = models.DateTimeField("Promotion end time", blank=True)

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ["name"]

    def __str__(self):
        return self.name
