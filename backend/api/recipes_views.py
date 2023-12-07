from rest_framework.viewsets import ModelViewSet

from .recipes_serializers import RecipeSerializer
from recipes.models import Recipe


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related("author").prefetch_related("ingredients")
    serializer_class = RecipeSerializer
