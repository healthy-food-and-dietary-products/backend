from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
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
from .recipes_views import RecipeViewSet
from .reviews_views import ReviewViewSet
from .users_views import (
    AddressViewSet,
    CustomTokenCreateView,
    CustomTokenDestroyView,
    CustomUserViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("subcategories", SubcategoryViewSet)
router.register("components", ComponentViewSet)
router.register("tags", TagViewSet)
router.register("producers", ProducerViewSet)
router.register("promotions", PromotionViewSet)
router.register("products", ProductViewSet)
router.register(
    r"products/(?P<product_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register("favorite-products", FavoriteProductViewSet)
router.register("users", CustomUserViewSet)
router.register(
    r"users/(?P<user_id>\d+)/addresses", AddressViewSet, basename="addresses"
)
router.register("shopping_cart", ShoppingCartViewSet, basename="shopping_carts")
router.register("order", OrderViewSet, basename="orders")
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("token/login/", CustomTokenCreateView.as_view(), name="login"),
    path("token/logout/", CustomTokenDestroyView.as_view(), name="logout"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="api:schema"),
        name="redoc",
    ),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Good Food API",
        default_version="v1",
        description="API documentation for the GoodFood project",
        contact=openapi.Contact(email="healthyfoodapi@yandex.ru"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
