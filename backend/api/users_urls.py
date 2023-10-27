from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .users_views import AddressViewSet, UserViewSet

router = DefaultRouter()
router.register("addresses", AddressViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
