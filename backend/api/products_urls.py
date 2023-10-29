from django.urls import include, path
from rest_framework.routers import DefaultRouter

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
from .users_views import AddressViewSet, AddressViewSetByID

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("subcategories", SubcategoryViewSet)
router.register("components", ComponentViewSet)
router.register("tags", TagViewSet)
router.register("producers", ProducerViewSet)
router.register("promotions", PromotionViewSet)
router.register("products", ProductViewSet)
router.register("favorites", FavoriteProductViewSet)
router.register("addresses", AddressViewSet, basename="addresses")
router.register(
    r"users/(?P<user_id>\d+)/addressesbyid",
    AddressViewSetByID,
    basename="addresses_by_id",
)


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
]
