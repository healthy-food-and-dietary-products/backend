from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views_products import (
    CategoryViewSet,
    ComponentViewSet,
    ProducerViewSet,
    ProductViewSet,
    PromotionViewSet,
    SubcategoryViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("subcategories", SubcategoryViewSet)
router.register("components", ComponentViewSet)
router.register("tags", TagViewSet)
router.register("producers", ProducerViewSet)
router.register("promotions", PromotionViewSet)
router.register("products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
