import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from tests.fixtures import (
    CATEGORY_NAME_1,
    CATEGORY_SLUG_1,
    INVALID_SLUG,
    INVALID_SLUG_MESSAGE,
    SUBCATEGORY_NAME_1,
)

TEST_NAME = "Test"
TEST_SLUG = "test"


@pytest.mark.django_db
def test_get_category_list(client, categories):
    response = client.get(reverse("api:category-list"))

    assert response.status_code == 200
    assert len(response.data) == 3
    assert response.data[0]["name"] == CATEGORY_NAME_1
    assert response.data[0]["slug"] == CATEGORY_SLUG_1
    assert response.data[0]["top_three_products"] == []


@pytest.mark.django_db
def test_get_category_by_id(client, categories, subcategories):
    response = client.get(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk})
    )

    assert response.status_code == 200
    assert response.data["name"] == CATEGORY_NAME_1
    assert response.data["slug"] == CATEGORY_SLUG_1
    assert len(response.data["subcategories"]) == 2
    assert response.data["subcategories"][0]["subcategory_name"] == SUBCATEGORY_NAME_1
    assert response.data["top_three_products"] == []


@pytest.mark.django_db
def test_create_category(auth_admin):
    payload = {"category_name": TEST_NAME}
    response = auth_admin.post(reverse("api:category-list"), payload)

    assert response.status_code == 201
    assert response.data["category_name"] == TEST_NAME
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_create_category_fail_if_not_admin(auth_client):
    payload = {"category_name": TEST_NAME}
    response = auth_client.post(reverse("api:category-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_category_fail_if_not_authenticated(client):
    payload = {"category_name": TEST_NAME}
    response = client.post(reverse("api:category-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_category_fail_name_validation(auth_admin):
    payload = {"name": TEST_NAME}
    response = auth_admin.post(reverse("api:category-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "category_name"


@pytest.mark.django_db
def test_create_category_fail_slug_validation(auth_admin):
    payload = {"category_name": TEST_NAME, "slug": INVALID_SLUG}
    response = auth_admin.post(reverse("api:category-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_edit_category_name(auth_admin, categories):
    payload = {"category_name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["category_name"] == TEST_NAME
    assert response.data["slug"] == categories[0].slug


@pytest.mark.django_db
def test_edit_category_slug(auth_admin, categories):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.patch(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["slug"] == TEST_SLUG
    assert response.data["category_name"] == categories[0].name


@pytest.mark.django_db
def test_edit_category_fail_if_not_admin(auth_client, categories):
    payload = {"category_name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_category_fail_if_not_authenticated(client, categories):
    payload = {"category_name": TEST_NAME}
    response = client.patch(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_category_fail_slug_validation(auth_admin, categories):
    payload = {"slug": INVALID_SLUG}
    response = auth_admin.patch(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_delete_category(auth_admin, categories):
    response = auth_admin.delete(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk})
    )

    assert response.status_code == 200
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_category_fail_if_not_admin(auth_client, categories):
    response = auth_client.delete(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk})
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_delete_category_fail_if_not_authenticated(client, categories):
    response = client.delete(
        reverse("api:category-detail", kwargs={"pk": categories[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
