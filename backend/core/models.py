from django.db import models
from django.utils.text import slugify


class CategoryModel(models.Model):
    """Abstract model for product categories and subcategories."""

    name = models.CharField("Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Makes slug from a category name."""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)[:50]
        super().save(*args, **kwargs)


class CreatedModel(models.Model):
    """Abstract model. Adds creation date."""

    pub_date = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        abstract = True