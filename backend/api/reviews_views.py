from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_standardized_errors.openapi_serializers import (
    ErrorResponse401Serializer,
    ErrorResponse403Serializer,
    ErrorResponse404Serializer,
    ValidationErrorResponseSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from .mixins import DestroyWithPayloadMixin
from .permissions import IsAuthorOrAdminOrReadOnly
from .products_views import STATUS_200_RESPONSE_ON_DELETE_IN_DOCS
from .reviews_serializers import ReviewSerializer, ReviewUserCheckSerializer
from products.models import Product
from reviews.models import Review


# TODO: write tests for reviews and for rating field in product views
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all product reviews",
        operation_description="Returns a list of all the reviews for a given product",
        responses={200: ReviewSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get review by id",
        operation_description="Retrieves a review by its id",
        responses={200: ReviewSerializer, 404: ErrorResponse404Serializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create review",
        operation_description="Creates a review (authorized only)",
        responses={
            201: ReviewSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponse401Serializer,
        },
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Edit review",
        operation_description="Edits a review by its id (author or admin)",
        responses={
            200: ReviewSerializer,
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
        operation_summary="Delete review",
        operation_description="Deletes a review by its id (author or admin)",
        responses={
            200: STATUS_200_RESPONSE_ON_DELETE_IN_DOCS,
            401: ErrorResponse401Serializer,
            403: ErrorResponse403Serializer,
            404: ErrorResponse404Serializer,
        },
    ),
)
class ReviewViewSet(DestroyWithPayloadMixin, viewsets.ModelViewSet):
    """Viewset for reviews."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Review.objects.select_related("product", "author")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "review_user_check":
            return ReviewUserCheckSerializer
        return ReviewSerializer

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

    @method_decorator(
        name="retrieve",
        decorator=swagger_auto_schema(
            operation_summary="Check user review",
            responses={200: ReviewUserCheckSerializer, 404: ErrorResponse404Serializer},
        ),
    )
    @action(
        methods=["get"],
        detail=False,
        url_path="review-user-check",
        permission_classes=[permissions.IsAuthenticated],
    )
    def review_user_check(self, request, product_id):
        """Shows whether the request.user has reviewed this product."""
        product = get_object_or_404(Product, id=int(product_id))
        serializer = self.get_serializer_class()
        payload = {
            "product": product_id,
            "user": self.request.user.pk,
            "reviewed": Review.objects.filter(
                author=self.request.user, product=product
            ).exists(),
        }
        return response.Response(
            serializer(
                payload,
                context={"request": request, "format": self.format_kwarg, "view": self},
            ).data,
            status=status.HTTP_200_OK,
        )
