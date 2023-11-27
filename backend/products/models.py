from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from core.models import CategoryModel
from users.models import User

MAX_PROMOTIONS_NUMBER = 1


class Category(CategoryModel):
    """Describes product categories."""

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["id"]


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
        ordering = ["id"]


class Component(models.Model):
    """Describes what the product consists of."""

    name = models.CharField(
        "Name", max_length=100, unique=True, help_text="Component name"
    )
    slug = models.SlugField(
        "Slug", max_length=100, unique=True, blank=True, help_text="Component slug"
    )

    class Meta:
        verbose_name = "Component"
        verbose_name_plural = "Components"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        """Makes slug from a component name."""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

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
        ordering = ["id"]

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
    slug = models.SlugField(
        "Slug", max_length=100, unique=True, blank=True, help_text="Producer slug"
    )
    producer_type = models.CharField(
        "Producer type", max_length=12, choices=CHOISES, default=COMPANY
    )
    description = models.TextField(
        "Description",
        blank=True,
        help_text="Brief information about the company or entrepreneur",
    )
    address = models.TextField("Address", help_text="Legal address of the producers")

    class Meta:
        verbose_name = "Producer"
        verbose_name_plural = "Producers"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        """Makes slug from a producer name."""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

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

    # TODO: make slug field after MVP?

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
        ordering = ["id"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Describes products."""

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
        return f"images/products/{self.pk}.jpg"

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
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Category",
    )
    # TODO: put choices so that only valid subcategories are displayed
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
        "Amount",
        validators=[MinValueValidator(1)],
        default=1,
        help_text="Number of grams, milliliters or items",
    )
    price = models.FloatField(
        "Price",
        validators=[MinValueValidator(0)],
        help_text="Price per one product unit",
    )
    promotions = models.ManyToManyField(
        Promotion,
        through="ProductPromotion",
        related_name="products",
        blank=True,
        verbose_name="Promotions",
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
    proteins = models.FloatField(
        "Proteins",
        validators=[MinValueValidator(0)],
        help_text="Number of proteins per 100 g of product",
    )
    fats = models.FloatField(
        "Fats",
        validators=[MinValueValidator(0)],
        help_text="Number of fats per 100 g of product",
    )
    carbohydrates = models.FloatField(
        "Carbohydrates",
        validators=[MinValueValidator(0)],
        help_text="Number of carbohydrates per 100 g of product",
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
        ordering = ["id"]

    @property
    def final_price(self):
        """
        Calculates the product price, including the max discount from its promotions.
        """
        if not self.promotions.all():
            return self.price
        discount = self.promotions.all()[0].discount
        return round(self.price * (1 - discount / 100), 2) if discount else self.price

    def is_favorited(self, user):
        """Checks whether the product is in the user's favorites."""
        return self.favorites.filter(user=user).exists()

    def clean_fields(self, exclude=None):
        """Checks that the category and subcategory fields match."""
        super().clean_fields(exclude=exclude)
        if self.subcategory.parent_category != self.category:
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
        ordering = ["id"]

    def __str__(self):
        return f"{self.user} added {self.product} to favorites"


class ProductPromotion(models.Model):
    """Describes connections between products and promotions."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "ProductPromotion"
        verbose_name_plural = "ProductPromotions"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "promotion"], name="unique_product_promotion"
            )
        ]
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Product {self.product} has promotion {self.promotion}"


@receiver(models.signals.post_save, sender=Product)
def check_promotion_quantity_after_product_save(sender, instance, **kwargs):
    """Checks promotion quantity of a product after product save."""
    if instance.promotions.count() > MAX_PROMOTIONS_NUMBER:
        raise ValidationError(
            "The number of promotions for one product "
            f"cannot exceed {MAX_PROMOTIONS_NUMBER}."
        )


@receiver(models.signals.post_save, sender=ProductPromotion)
def check_promotion_quantity_after_product_promotion_save(sender, instance, **kwargs):
    """Checks promotion quantity of a product after product_promotion save."""
    if instance.product.promotions.count() > MAX_PROMOTIONS_NUMBER:
        raise ValidationError(
            "The number of promotions for one product "
            f"cannot exceed {MAX_PROMOTIONS_NUMBER}."
        )
