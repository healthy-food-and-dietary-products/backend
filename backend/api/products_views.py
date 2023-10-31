from django.shortcuts import get_object_or_404
from django_filters import rest_framework as rf_filters
from rest_framework import decorators, permissions, response, status, viewsets

from .filters import ProductFilter
from .permissions import IsAdmin, IsAdminOrReadOnly
from .products_serializers import (
    CategoryCreateSerializer,
    CategorySerializer,
    ComponentSerializer,
    FavoriteProductSerializer,
    ProducerSerializer,
    ProductCreateSerializer,
    ProductLightSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
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
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "create":
            return CategoryCreateSerializer
        if self.action == "partial_update":
            return CategoryCreateSerializer
        return CategorySerializer


class SubcategoryViewSet(viewsets.ModelViewSet):
    """Viewset for subcategories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class ComponentViewSet(viewsets.ModelViewSet):
    """Viewset for components."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Viewset for tags."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class ProducerViewSet(viewsets.ModelViewSet):
    """Viewset for producers."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class PromotionViewSet(viewsets.ModelViewSet):
    """Viewset for promotions."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class ProductViewSet(viewsets.ModelViewSet):
    """Viewset for products."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.action == "create":
            return ProductCreateSerializer
        if self.action == "partial_update":
            return ProductUpdateSerializer
        return ProductSerializer

    def create_delete_or_scold(self, model, product, request):
        instance = model.objects.filter(product=product, user=request.user)
        if request.method == "DELETE" and not instance:
            return response.Response(
                {"errors": "Этого продукта не было в вашем списке Избранного."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "DELETE":
            instance.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        if instance:
            return response.Response(
                {"errors": "Этот продукт уже есть в вашем списке Избранного."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=request.user, product=product)
        serializer = ProductLightSerializer(
            product,
            context={"request": request, "format": self.format_kwarg, "view": self},
        )
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        subcategory_id = serializer._kwargs["data"]["subcategory"]
        subcategory = Subcategory.objects.get(id=subcategory_id)
        serializer.save(category=subcategory.parent_category)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        subcategory_id = serializer._kwargs["data"].get("subcategory")
        if subcategory_id:
            subcategory = Subcategory.objects.get(id=subcategory_id)
            serializer.save(category=subcategory.parent_category)
        return super().perform_update(serializer)

    def retrieve(self, request, *args, **kwargs):
        """Increments the views_number field when someone views this product."""
        obj = self.get_object()
        obj.views_number += 1
        obj.save(update_fields=("views_number",))
        return super().retrieve(request, *args, **kwargs)

    @decorators.action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        return self.create_delete_or_scold(FavoriteProduct, product, request)


class FavoriteProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for viewing useres' favorite products by admins."""

    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAdmin]
    pagination_class = None
