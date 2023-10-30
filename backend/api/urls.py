from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .orders_views import OrderViewSet, ShoppingCartViewSet
from .products_views import (
    CategoryViewSet,
    ComponentViewSet,
    FavoriteProductViewSet,
    ProducerViewSet,
    ProductViewSet,
    PromotionViewSet,
    SubcategoryViewSet,
    TagViewSet,
)
from .users_views import AddressViewSet, UserViewSet

app_name = "api"

router = DefaultRouter()
router.register("addresses", AddressViewSet)
router.register("users", UserViewSet)
router.register("shopping_cart", ShoppingCartViewSet),
router.register("order", OrderViewSet)
router.register("categories", CategoryViewSet)
router.register("subcategories", SubcategoryViewSet)
router.register("components", ComponentViewSet)
router.register("tags", TagViewSet)
router.register("producers", ProducerViewSet)
router.register("promotions", PromotionViewSet)
router.register("products", ProductViewSet)
router.register("favorite-products", FavoriteProductViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
