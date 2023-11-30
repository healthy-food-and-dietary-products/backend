from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models import Product
from users.models import User


class Review(models.Model):
    """Describes customer reviews on products."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Product",
    )
    text = models.TextField(verbose_name="Text", blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Author",
    )
    score = models.PositiveSmallIntegerField(
        "Score", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    # TODO: if user edit review, pub_date should be updated
    # (but user can't edit pubdate, it should be updated automaticly on api level)
    pub_date = models.DateTimeField("Publication Date", auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=("product", "author"), name="unique_product_author"
            )
        ]

    def __str__(self):
        return self.text
