from rest_framework.viewsets import ReadOnlyModelViewSet

from .recipes_serializers import RecipeSerializer
from recipes.models import Recipe


class RecipeViewSet(ReadOnlyModelViewSet):
    queryset = RecipeSerializer.setup_eager_loading(Recipe.objects.all())
    serializer_class = RecipeSerializer
