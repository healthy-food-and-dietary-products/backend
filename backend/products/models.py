from django.db import models

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
