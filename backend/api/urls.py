from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ShoppingCartViewSet
)

app_name = 'api'

router = DefaultRouter()




router.register(
    r'shopping_cart', ShoppingCartViewSet, basename='shopping_carts')


urlpatterns = [
    path('', include(router.urls)),

]
