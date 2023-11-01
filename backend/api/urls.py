from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .orders_views import ShoppingCartViewSet
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

# from .users_views import AddressViewSet

app_name = "api"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
# router.register("shopping_cart", ShoppingCartViewSet),
router.register("subcategories", SubcategoryViewSet)
router.register("components", ComponentViewSet)
router.register("tags", TagViewSet)
router.register("producers", ProducerViewSet)
router.register("promotions", PromotionViewSet)
router.register("products", ProductViewSet)
router.register("favorite-products", FavoriteProductViewSet)
# router.register(
#     r"users/(?P<user_id>\d+)/addresses", AddressViewSet, basename="addresses"
# )

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
]
