from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters import rest_framework as rf_filters

from products.models import Product


class ProductFilter(rf_filters.FilterSet):
    """Class for filtering products."""

    name = rf_filters.CharFilter(method="startswith_contains_union_method")
    category = rf_filters.CharFilter(field_name="category__slug")
    subcategory = rf_filters.CharFilter(field_name="subcategory__slug")
    producer = rf_filters.CharFilter(field_name="producer__slug")
    tags = rf_filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = rf_filters.NumberFilter(method="product_boolean_methods")

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "subcategory",
            "producer",
            "tags",
            "promotions",
            "discontinued",
            "is_favorited",
        ]

    def startswith_contains_union_method(self, queryset, name, value):
        if not bool(value):
            return queryset
        startswith_lookup = "__".join([name, "istartswith"])
        contains_lookup = "__".join([name, "icontains"])
        return (
            queryset.filter(
                Q(**{startswith_lookup: value}) | Q(**{contains_lookup: value})
            )
            .annotate(
                is_start=ExpressionWrapper(
                    Q(**{startswith_lookup: value}), output_field=BooleanField()
                )
            )
            .order_by("-is_start")
        )

    def product_boolean_methods(self, queryset, name, value):
        if not bool(value):
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        product_ids = [r.pk for r in queryset if getattr(r, name)(user) == value]
        if product_ids:
            return queryset.filter(pk__in=product_ids)
        return queryset.none()
