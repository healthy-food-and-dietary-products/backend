from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import CategoryModel
from users.models import User


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
    discount = models.PositiveSmallIntegerField(
        "Discount",
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Percentage of a product price",
        error_messages={"invalid": "Допустимы числа от 0 до 100"},
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
    start_time = models.DateTimeField("Promotion start time", null=True, blank=True)
    end_time = models.DateTimeField("Promotion end time", null=True, blank=True)

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Describes products."""

    MAX_PROMOTIONS_NUMBER = 1

    GRAMS = "grams"
    MILLILITRES = "milliliters"
    ITEMS = "items"

    CHOISES = [
        (GRAMS, "г."),
        (MILLILITRES, "мл."),
        (ITEMS, "шт."),
    ]

    def product_directory_path(self, filename):
        """Constructs the path which the product photo will be saved."""
        return f"images/products/{self.pk}"

    name = models.CharField(
        "Name", max_length=100, unique=True, help_text="Product name"
    )
    description = models.TextField(
        "Description", blank=True, help_text="Product description"
    )
    creation_time = models.DateTimeField(
        "Creation time",
        auto_now_add=True,
        help_text="Date of inclusion of the product in the database",
    )
    categorу = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Category",
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Subcategory",
    )
    tags = models.ManyToManyField(
        Tag, related_name="products", blank=True, verbose_name="Tags"
    )
    discontinued = models.BooleanField(
        "Discontinued",
        default=False,
        help_text="Is this product discontinued from sale",
    )
    producer = models.ForeignKey(
        Producer,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Producer",
    )
    measure_unit = models.CharField(
        "Measure unit", max_length=11, choices=CHOISES, default=ITEMS
    )
    amount = models.PositiveSmallIntegerField(
        "Amount", default=1, help_text="Number of grams, milliliters or items"
    )
    price = models.FloatField("Price", help_text="Price per one product unit")
    promotions = models.ManyToManyField(
        Promotion, related_name="products", blank=True, verbose_name="Promotions"
    )
    promotion_quantity = models.PositiveSmallIntegerField(
        "Promotion quantity",
        default=0,
        validators=[MaxValueValidator(MAX_PROMOTIONS_NUMBER)],
        error_messages={"invalid": f"Допустимы числа от 0 до {MAX_PROMOTIONS_NUMBER}"},
        help_text="Number of promotions valid for this product",
    )
    photo = models.ImageField("Photo", blank=True, upload_to=product_directory_path)
    components = models.ManyToManyField(
        Component,
        related_name="products",
        verbose_name="Components that the product consists of",
    )
    kcal = models.PositiveSmallIntegerField(
        "Kcal", help_text="Number of kcal per 100 g of product"
    )
    proteins = models.PositiveSmallIntegerField(
        "Proteins", help_text="Number of proteins per 100 g of product"
    )
    fats = models.PositiveSmallIntegerField(
        "Fats", help_text="Number of fats per 100 g of product"
    )
    carbohydrates = models.PositiveSmallIntegerField(
        "Carbohydrates", help_text="Number of carbohydrates per 100 g of product"
    )
    views_number = models.PositiveIntegerField(
        "Views number", default=0, help_text="Number of product page views"
    )
    orders_number = models.PositiveIntegerField(
        "Orders number", default=0, help_text="Number of orders for this product"
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    @property
    def final_price(self):
        """
        Calculates the product price, including the max discount from its promotions.
        """
        max_discount = self.promotions.aggregate(models.Max("discount"))[
            "discount__max"
        ]
        return self.price * (1 - max_discount / 100) if max_discount else self.price

    def clean_fields(self, exclude=None):
        """Checks that the category and subcategory fields match."""
        super().clean_fields(exclude=exclude)
        if self.subcategory.parent_category != self.categorу:
            raise ValidationError("Subcategory does not match category")

    def __str__(self):
        return self.name

    # TODO: add expiration_date field and quantity fields (in future if necessary)


class FavoriteProduct(models.Model):
    """Describes favorite products."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites", verbose_name="User"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Product",
    )

    class Meta:
        verbose_name = "Favorite Product"
        verbose_name_plural = "Favorite Products"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_favorite_user"
            )
        ]

    def __str__(self):
        return f"{self.user} added {self.product} to favorites"
