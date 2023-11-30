from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets

from .mixins import DestroyWithPayloadMixin
from .permissions import IsAuthorOrAdminOrReadOnly
from .reviews_serializers import ReviewSerializer
from products.models import Product
from reviews.models import Review


# TODO: Set possible responses for api docs
# TODO: write tests for reviews and for rating field in product views
class ReviewViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for reviews."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Review.objects.select_related("product", "author")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(
            product__id=self.kwargs.get("product_id")
        ).select_related("product", "author")

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.kwargs.get("product_id"))
        serializer.save(author=self.request.user, product=product)

    def perform_update(self, serializer):
        serializer.save(pub_date=timezone.now(), was_edited=True)
        return super().perform_update(serializer)
