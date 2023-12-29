from django.utils.decorators import method_decorator
from drf_standardized_errors.openapi_serializers import ErrorResponse404Serializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ReadOnlyModelViewSet

from .recipes_serializers import RecipeSerializer
from recipes.models import Recipe


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List all recipes",
        operation_description=("Returns a list of all the recipes"),
        responses={200: RecipeSerializer},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Get recipe by id",
        operation_description=("Retrieves a recipe by its id"),
        responses={200: RecipeSerializer, 404: ErrorResponse404Serializer},
    ),
)
class RecipeViewSet(ReadOnlyModelViewSet):
    queryset = RecipeSerializer.setup_eager_loading(Recipe.objects.all())
    serializer_class = RecipeSerializer
