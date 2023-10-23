from rest_framework import viewsets

from .permissions_products import IsAdminOrReadOnly
from .serializers_products import (
    CategorySerializer,
    ComponentSerializer,
    ProducerSerializer,
    PromotionSerializer,
    SubcategorySerializer,
    TagSerializer,
)
from products.models import Category, Component, Producer, Promotion, Subcategory, Tag


class CategoryViewSet(viewsets.ModelViewSet):
    """Viewset for categories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]


class SubcategoryViewSet(viewsets.ModelViewSet):
    """Viewset for subcategories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]


class ComponentViewSet(viewsets.ModelViewSet):
    """Viewset for components."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]


class TagViewSet(viewsets.ModelViewSet):
    """Viewset for tags."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]


class ProducerViewSet(viewsets.ModelViewSet):
    """Viewset for producers."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]


class PromotionViewSet(viewsets.ModelViewSet):
    """Viewset for promotions."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]
