from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters import rest_framework as rf_filters

from products.models import Product


class CharFilterInFilter(rf_filters.BaseInFilter, rf_filters.CharFilter):
    """Custom char filter allowing comma-separated incoming values."""

    pass


class ProductFilter(rf_filters.FilterSet):
    """Class for filtering products."""

    name = rf_filters.CharFilter(method="startswith_contains_union_method")
    category = CharFilterInFilter(field_name="category__slug")
    subcategory = CharFilterInFilter(field_name="subcategory__slug")
    producer = CharFilterInFilter(field_name="producer__slug")
    components = CharFilterInFilter(field_name="components__slug")
    tags = CharFilterInFilter(field_name="tags__slug")
    promotions = CharFilterInFilter(field_name="promotions__slug")
    is_favorited = rf_filters.NumberFilter(method="product_boolean_methods")
    min_price = rf_filters.NumberFilter(method="get_min_price")
    max_price = rf_filters.NumberFilter(method="get_max_price")

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "subcategory",
            "producer",
            "components",
            "tags",
            "promotions",
            "discontinued",
            "is_favorited",
            "min_price",
            "max_price",
        ]

    def startswith_contains_union_method(self, queryset, name, value):
        """
        When using sqlite DB, filtering by name will be case-sensitive;
        when using PostgreSQL DB, filtering by name will be case-insensitive
        as it should be.
        """
        if not bool(value):
            return queryset
        return (
            queryset.filter(Q(name__istartswith=value) | Q(name__icontains=value))
            .annotate(
                is_start=ExpressionWrapper(
                    Q(name__istartswith=value), output_field=BooleanField()
                )
            )
            .order_by("-is_start")
        )

    def product_boolean_methods(self, queryset, name, value):
        if value not in [0, 1]:
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        product_ids = [obj.pk for obj in queryset if getattr(obj, name)(user) == value]
        if product_ids:
            return queryset.filter(pk__in=product_ids)
        return queryset.none()

    def get_min_price(self, queryset, name, value):
        if value <= 0:
            return queryset
        product_ids = [obj.pk for obj in queryset if obj.final_price >= value]
        if product_ids:
            return queryset.filter(pk__in=product_ids)
        return queryset.none()

    def get_max_price(self, queryset, name, value):
        if value <= 0:
            return queryset
        product_ids = [obj.pk for obj in queryset if obj.final_price <= value]
        if product_ids:
            return queryset.filter(pk__in=product_ids)
        return queryset.none()
