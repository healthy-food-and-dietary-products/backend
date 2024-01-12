import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from api.products_views import (
    DOUBLE_FAVORITE_PRODUCT_ERROR_MESSAGE,
    NO_FAVORITE_PRODUCT_ERROR_MESSAGE,
)
from tests.fixtures import TEST_NUMBER

# TODO: test is_favorited in top_3_products field


@pytest.mark.django_db
def test_get_favorite_list(auth_admin, favorites, user, products):
    response = auth_admin.get(reverse("api:favoriteproduct-list"))

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["user"]["id"] == user.pk
    assert response.data[0]["user"]["username"] == user.username
    assert response.data[0]["product"]["name"] == products[0].name


@pytest.mark.django_db
def test_get_favorite_by_id(auth_admin, favorites, user, products):
    response = auth_admin.get(
        reverse("api:favoriteproduct-detail", kwargs={"pk": favorites[0].pk})
    )

    assert response.status_code == 200
    assert response.data["user"]["id"] == user.pk
    assert response.data["user"]["username"] == user.username
    assert response.data["product"]["name"] == products[0].name


@pytest.mark.django_db
def test_get_favorite_list_fail_if_not_admin(auth_client):
    response = auth_client.get(reverse("api:favoriteproduct-list"))

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_get_favorite_list_fail_if_not_authenticated(client):
    response = client.get(reverse("api:favoriteproduct-list"))

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_get_favorite_by_id_fail_if_not_admin(auth_client, favorites):
    response = auth_client.get(
        reverse("api:favoriteproduct-detail", kwargs={"pk": favorites[0].pk})
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_get_favorite_by_id_fail_if_not_authenticated(client, favorites):
    response = client.get(
        reverse("api:favoriteproduct-detail", kwargs={"pk": favorites[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_get_favorite_by_id_fail_404(auth_admin, favorites):
    response = auth_admin.get(
        reverse("api:favoriteproduct-detail", kwargs={"pk": TEST_NUMBER})
    )

    assert response.status_code == 404
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_found"


@pytest.mark.django_db
def test_create_favorite(auth_client, products, user):
    response = auth_client.post(
        reverse("api:product-favorite", kwargs={"pk": products[0].pk})
    )

    assert response.status_code == 201
    assert response.data["user"]["id"] == user.pk
    assert response.data["user"]["username"] == user.username
    assert response.data["product"]["name"] == products[0].name


@pytest.mark.django_db
def test_create_favorite_fail_if_duplication(auth_client, products, favorites):
    response = auth_client.post(
        reverse("api:product-favorite", kwargs={"pk": products[0].pk})
    )

    assert response.status_code == 400
    assert response.data["errors"][0]["detail"] == DOUBLE_FAVORITE_PRODUCT_ERROR_MESSAGE


@pytest.mark.django_db
def test_create_favorite_fail_if_not_authenticated(client, products):
    response = client.post(
        reverse("api:product-favorite", kwargs={"pk": products[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_favorite_fail_404(auth_client):
    response = auth_client.post(
        reverse("api:product-favorite", kwargs={"pk": TEST_NUMBER})
    )

    assert response.status_code == 404
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_found"


@pytest.mark.django_db
def test_delete_favorite(auth_client, products, user, favorites):
    response = auth_client.delete(
        reverse("api:product-favorite", kwargs={"pk": products[0].pk})
    )

    assert response.status_code == 200
    assert response.data["favorite_product_object_id"] == 1
    assert response.data["favorite_product_id"] == products[0].pk
    assert response.data["favorite_product_name"] == products[0].name
    assert response.data["user_id"] == user.pk
    assert response.data["user_username"] == user.username
    assert response.data["success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_favorite_fail_if_no_such_favorite(auth_client, products):
    response = auth_client.delete(
        reverse("api:product-favorite", kwargs={"pk": products[0].pk})
    )

    assert response.status_code == 400
    assert response.data["errors"][0]["detail"] == NO_FAVORITE_PRODUCT_ERROR_MESSAGE


@pytest.mark.django_db
def test_delete_favorite_fail_if_not_authenticated(client, products):
    response = client.delete(
        reverse("api:product-favorite", kwargs={"pk": products[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_delete_favorite_fail_404(auth_client):
    response = auth_client.delete(
        reverse("api:product-favorite", kwargs={"pk": TEST_NUMBER})
    )

    assert response.status_code == 404
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_found"
