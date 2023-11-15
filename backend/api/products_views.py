from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as rf_filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import decorators, permissions, response, status, viewsets

from .filters import ProductFilter
from .mixins import DestroyWithPayloadMixin
from .pagination import CustomPageNumberPagination
from .permissions import IsAdmin, IsAdminOrReadOnly
from .products_serializers import (
    CategoryCreateSerializer,
    CategorySerializer,
    ComponentSerializer,
    FavoriteProductCreateSerializer,
    FavoriteProductSerializer,
    ProducerSerializer,
    ProductCreateSerializer,
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


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List all categories",
    operation_description="This endpoint returns a list of all the categories",
    responses={200: CategorySerializer, 302: 'something', '400': 'bad'}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="List all categories",
    operation_description="This endpoint returns a list of all the categories",
    responses={200: 'good', 302: 'something', '404': 'not found'}
))
class CategoryViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for categories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return CategoryCreateSerializer
        if self.action == "partial_update":
            return CategoryCreateSerializer
        return CategorySerializer


class SubcategoryViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for subcategories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ComponentViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for components."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [IsAdminOrReadOnly]


class TagViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for tags."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProducerViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for producers."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [IsAdminOrReadOnly]


class PromotionViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for promotions."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for products."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == "create":
            return ProductCreateSerializer
        if self.action == "partial_update":
            return ProductUpdateSerializer
        if self.action == "favorite":
            return FavoriteProductCreateSerializer
        return ProductSerializer

    @transaction.atomic
    def create_delete_or_scold(self, model, product, request):
        instance = model.objects.filter(product=product, user=request.user)
        if request.method == "DELETE" and not instance:
            return response.Response(
                {"errors": "Этого продукта не было в вашем списке Избранного."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "DELETE":
            message = {
                "favorite_product_object_id": instance[0].id,
                "favorite_product_id": instance[0].product.id,
                "favorite_product_name": instance[0].product.name,
                "user_id": instance[0].user.id,
                "user_username": instance[0].user.username,
                "Success": "This favorite product object was successfully deleted",
            }
            instance.delete()
            return response.Response(data=message, status=status.HTTP_200_OK)
        if instance:
            return response.Response(
                {"errors": "Этот продукт уже есть в вашем списке Избранного."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_favorite_product = model.objects.create(user=request.user, product=product)
        serializer = FavoriteProductSerializer(
            new_favorite_product,
            context={"request": request, "format": self.format_kwarg, "view": self},
        )
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def perform_create(self, serializer):
        subcategory_id = serializer._kwargs["data"]["subcategory"]
        subcategory = Subcategory.objects.get(id=subcategory_id)
        serializer.save(category=subcategory.parent_category)
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_update(self, serializer):
        subcategory_id = serializer._kwargs["data"].get("subcategory")
        if subcategory_id:
            subcategory = Subcategory.objects.get(id=subcategory_id)
            serializer.save(category=subcategory.parent_category)
        return super().perform_update(serializer)

    @transaction.atomic
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
