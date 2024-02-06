from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as rf_filters
from drf_standardized_errors.openapi_serializers import (
    ClientErrorEnum,
    ErrorCode406Enum,
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ErrorResponse404Serializer,
    ErrorResponse406Serializer,
    ValidationErrorResponseSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, response, status, viewsets
from rest_framework.decorators import action

from .filters import ProductFilter
from .mixins import MESSAGE_ON_DELETE, DestroyWithPayloadMixin
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrReadOnly
from .products_serializers import (
    CategoryBriefSerializer,
    CategoryCreateSerializer,
    CategorySerializer,
    ComponentSerializer,
    CouponSerializer,
    FavoriteProductCreateSerializer,
    FavoriteProductDeleteSerializer,
    FavoriteProductSerializer,
    ProducerSerializer,
    ProductCreateSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
    ProductUserOrderCheckSerializer,
    PromotionSerializer,
    SubcategorySerializer,
    TagSerializer,
)
from orders.models import OrderProduct
from products.models import (
    Category,
    Component,
    Coupon,
    FavoriteProduct,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)

NO_FAVORITE_PRODUCT_ERROR_MESSAGE = "Этого продукта не было в вашем списке Избранного."
DOUBLE_FAVORITE_PRODUCT_ERROR_MESSAGE = (
    "Этот продукт уже есть в вашем списке Избранного."
)
STATUS_200_RESPONSE_ON_DELETE_IN_DOCS = (
    "Detailed information about the deleted object and a success message"
)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="Returns a list of all the categories",
        responses={200: CategorySerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get category by id",
        operation_description="Retrieves a category by its id",
        responses={200: CategorySerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create category",
        operation_description="Creates a category (admin only)",
        responses={
            201: CategoryCreateSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit category",
        operation_description="Edits a category by its id (admin only)",
        responses={
            200: CategoryCreateSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete category",
        operation_description="Deletes a category by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="category_brief_list",
    decorator=swagger_auto_schema(
        operation_summary="List categories brief info",
        responses={200: CategoryBriefSerializer},
    ),
)
@method_decorator(
    name="category_brief_detail",
    decorator=swagger_auto_schema(
        operation_summary="Show brief category info",
        responses={200: CategoryBriefSerializer, 404: ErrorResponse404Serializer},
    ),
)
class CategoryViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for categories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return CategoryCreateSerializer
        if self.action in ["category_brief_list", "category_brief_detail"]:
            return CategoryBriefSerializer
        return CategorySerializer

    def get_queryset(self):
        return CategorySerializer.setup_eager_loading(
            Category.objects.all(), self.request.user
        )

    # TODO: test this endpoint
    @action(methods=["get"], detail=False, url_path="category-brief-list")
    def category_brief_list(self, request):
        """
        Shows brief information about categories without indicating subcategories
        and top products of these categories.
        """
        categories_list = Category.objects.all()
        serializer = self.get_serializer_class()
        return response.Response(
            serializer(
                categories_list,
                many=True,
                context={"request": request, "format": self.format_kwarg, "view": self},
            ).data,
            status=status.HTTP_200_OK,
        )

    # TODO: test this endpoint
    @action(methods=["get"], detail=True, url_path="category-brief-detail")
    def category_brief_detail(self, request, pk):
        """
        Shows brief information about a category without indicating subcategories
        and top products of that category.
        """
        category = get_object_or_404(Category, id=pk)
        serializer = self.get_serializer_class()
        return response.Response(
            serializer(
                category,
                context={"request": request, "format": self.format_kwarg, "view": self},
            ).data,
            status=status.HTTP_200_OK,
        )


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all subcategories",
        operation_description="Returns a list of all the subcategories",
        responses={200: SubcategorySerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get subcategory by id",
        operation_description="Retrieves a subcategory by its id",
        responses={200: SubcategorySerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create subcategory",
        operation_description="Creates a subcategory (admin only)",
        responses={
            201: SubcategorySerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit subcategory",
        operation_description="Edits a subcategory by its id (admin only)",
        responses={
            200: SubcategorySerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete subcategory",
        operation_description="Deletes a subcategory by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class SubcategoryViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for subcategories."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Subcategory.objects.select_related("parent_category").all()
    serializer_class = SubcategorySerializer
    permission_classes = [IsAdminOrReadOnly]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all components",
        operation_description="Returns a list of all the components",
        responses={200: ComponentSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get component by id",
        operation_description="Retrieves a component by its id",
        responses={200: ComponentSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create component",
        operation_description="Creates a component (admin only)",
        responses={
            201: ComponentSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit component",
        operation_description="Edits a component by its id (admin only)",
        responses={
            200: ComponentSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete component",
        operation_description="Deletes a component by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class ComponentViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for components."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [IsAdminOrReadOnly]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all tags",
        operation_description="Returns a list of all the tags",
        responses={200: TagSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get tag by id",
        operation_description="Retrieves a tag by its id",
        responses={200: TagSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create tag",
        operation_description="Creates a tag (admin only)",
        responses={
            201: TagSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit tag",
        operation_description="Edits a tag by its id (admin only)",
        responses={
            200: TagSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete tag",
        operation_description="Deletes a tag by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class TagViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for tags."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return TagSerializer.setup_eager_loading(Tag.objects.all(), self.request.user)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all producers",
        operation_description="Returns a list of all the producers",
        responses={200: ProducerSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get producer by id",
        operation_description="Retrieves a producer by its id",
        responses={200: ProducerSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create producer",
        operation_description="Creates a producer (admin only)",
        responses={
            201: ProducerSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit producer",
        operation_description="Edits a producer by its id (admin only)",
        responses={
            200: ProducerSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete producer",
        operation_description="Deletes a producer by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class ProducerViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for producers."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [IsAdminOrReadOnly]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all promotions",
        operation_description="Returns a list of all the promotions",
        responses={200: PromotionSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get promotion by id",
        operation_description="Retrieves a promotion by its id",
        responses={200: PromotionSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create promotion",
        operation_description="Creates a promotion (admin only)",
        responses={
            201: PromotionSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit promotion",
        operation_description="Edits a promotion by its id (admin only)",
        responses={
            200: PromotionSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete promotion",
        operation_description="Deletes a promotion by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class PromotionViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for promotions."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminOrReadOnly]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all coupons",
        operation_description="Returns a list of all the coupons",
        responses={200: CouponSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get coupon by id",
        operation_description="Retrieves a coupon by its id",
        responses={200: CouponSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create coupon",
        operation_description="Creates a coupon (admin only)",
        responses={
            201: CouponSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit coupon",
        operation_description="Edits a coupon by its id (admin only)",
        responses={
            200: CouponSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete coupon",
        operation_description="Deletes a coupon by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class CouponViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for coupons."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrReadOnly]

    @transaction.atomic
    def perform_create(self, serializer):
        """Sets the correct promotion_type during coupon creation."""
        serializer.save(promotion_type=Promotion.COUPON)
        return super().perform_create(serializer)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all products",
        operation_description="Returns a list of all the products",
        responses={200: ProductSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get product by id",
        operation_description="Retrieves a product by its id",
        responses={200: ProductSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create product",
        operation_description="Creates a product (admin only)",
        responses={
            201: ProductCreateSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit product",
        operation_description="Edits a product by its id (admin only)",
        responses={
            200: PromotionSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete product",
        operation_description="Deletes a product by its id (admin only)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class ProductViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for products."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [rf_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering = ["pk"]
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == "create":
            return ProductCreateSerializer
        if self.action == "partial_update":
            return ProductUpdateSerializer
        if self.action == "favorite":
            return FavoriteProductCreateSerializer
        if self.action == "order_user_check":
            return ProductUserOrderCheckSerializer
        return ProductSerializer

    def get_queryset(self):
        return ProductSerializer.setup_eager_loading(
            Product.objects.all(), self.request.user
        )

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Sets the correct category for the given subcategory during product creation.
        """
        subcategory_id = serializer._kwargs["data"]["subcategory"]
        subcategory = Subcategory.objects.get(id=subcategory_id)
        serializer.save(category=subcategory.parent_category)
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Sets the correct category for the given subcategory during product editing.
        """
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

    @swagger_auto_schema(
        method="post",
        operation_summary="Add favorite product",
        operation_description=(
            "Adds a product to a user's favorites (authorized user only)"
        ),
        responses={
            201: FavoriteProductSerializer,
            400: ErrorResponse406Serializer,
            401: ErrorResponse401Serializer,
            404: ErrorResponse404Serializer,
        },
    )
    @swagger_auto_schema(
        method="delete",
        operation_summary="Delete favorite product",
        operation_description=(
            "Deletes a product from a user's favorites (authorized user only)"
        ),
        responses={
            200: FavoriteProductDeleteSerializer,
            400: ErrorResponse406Serializer,
            401: ErrorResponse401Serializer,
            404: ErrorResponse404Serializer,
        },
    )
    @transaction.atomic
    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        favorite_product = FavoriteProduct.objects.filter(
            product=product, user=request.user
        )
        if request.method == "DELETE" and not favorite_product:
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode406Enum.NOT_ACCEPTABLE,
                        "detail": NO_FAVORITE_PRODUCT_ERROR_MESSAGE,
                    }
                ],
            }
            return response.Response(
                ErrorResponse406Serializer(payload).data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "DELETE":
            payload = {
                "favorite_product_object_id": favorite_product[0].id,
                "favorite_product_id": product.id,
                "favorite_product_name": product.name,
                "user_id": request.user.id,
                "user_username": request.user.username,
                "success": MESSAGE_ON_DELETE,
            }
            favorite_product.delete()
            return response.Response(
                FavoriteProductDeleteSerializer(payload).data, status=status.HTTP_200_OK
            )
        if favorite_product:
            payload = {
                "type": ClientErrorEnum.CLIENT_ERROR,
                "errors": [
                    {
                        "code": ErrorCode406Enum.NOT_ACCEPTABLE,
                        "detail": DOUBLE_FAVORITE_PRODUCT_ERROR_MESSAGE,
                    }
                ],
            }
            return response.Response(
                ErrorResponse406Serializer(payload).data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_favorite_product = FavoriteProduct.objects.create(
            user=request.user, product=product
        )
        serializer = FavoriteProductSerializer(
            new_favorite_product,
            context={"request": request, "format": self.format_kwarg, "view": self},
        )
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    # TODO: test this endpoint
    @method_decorator(
        name="retrieve",
        decorator=swagger_auto_schema(
            operation_summary="Check user product order",
            responses={
                200: ProductUserOrderCheckSerializer,
                404: ErrorResponse404Serializer,
            },
        ),
    )
    @action(
        methods=["get"],
        detail=True,
        url_path="order-user-check",
        permission_classes=[permissions.IsAuthenticated],
    )
    def order_user_check(self, request, pk):
        """Shows whether the request.user has ordered this product."""
        product = get_object_or_404(Product, id=int(pk))
        serializer = self.get_serializer_class()
        payload = {
            "product": pk,
            "user": self.request.user.pk,
            "ordered": OrderProduct.objects.filter(
                product=product, order__user=self.request.user
            ).exists(),
        }
        return response.Response(
            serializer(
                payload,
                context={"request": request, "format": self.format_kwarg, "view": self},
            ).data,
            status=status.HTTP_200_OK,
        )


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all favorite products",
        operation_description=(
            "Returns a list of all the favorite products of all users (admin only)"
        ),
        responses={
            200: FavoriteProductSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
        },
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get favorite product by id",
        operation_description=(
            "Retrieves a record about the user and his or her favorite product "
            "by id of this record (admin only)"
        ),
        responses={
            200: FavoriteProductSerializer,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class FavoriteProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for viewing useres' favorite products by admins."""

    queryset = FavoriteProduct.objects.select_related("user", "product")
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAdminUser]
