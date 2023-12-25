from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Class to display product reviews in admin panel."""

    list_display = [
        "pk",
        "product",
        "author",
        "score",
        "pub_date",
        "text",
        "was_edited",
    ]
    list_display_links = ("product",)
    fields = ["product", "author", "score", "pub_date", "was_edited", "text"]
    readonly_fields = ["pub_date", "was_edited"]
    search_fields = ["product__name", "author__username", "text"]
    list_filter = ["score", "pub_date", "product", "author", "was_edited"]
    ordering = ["pk"]
