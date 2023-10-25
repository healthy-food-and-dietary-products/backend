from rest_framework import viewsets

# from .permissions import IsAuthorOnly
from .permissions_products import IsAdminOrReadOnly
from .serializers_products import (
    CategorySerializer,
    ComponentSerializer,
    FavoriteProductSerializer,
    ProducerSerializer,
    ProductSerializer,
    PromotionSerializer,
    SubcategorySerializer,
    TagSerializer,
)
from products.models import (
    Category,
    Component,
    FavoriteProduct,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)


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


class ProductViewSet(viewsets.ModelViewSet):
    """Viewset for products."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]


class FavoriteProductViewSet(viewsets.ModelViewSet):
    """Viewset for favorite products."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        # IsAuthorOnly,
        IsAdminOrReadOnly,
    ]
