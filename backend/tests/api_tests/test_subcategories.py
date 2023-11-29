import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from tests.fixtures import (
    INVALID_ID,
    INVALID_SLUG,
    INVALID_SLUG_MESSAGE,
    SUBCATEGORY_NAME_1,
    SUBCATEGORY_SLUG_1,
    TEST_NAME,
    TEST_SLUG,
)


@pytest.mark.django_db
def test_get_subcategory_list(client, subcategories):
    response = client.get(reverse("api:subcategory-list"))

    assert response.status_code == 200
    assert len(response.data) == 4
    assert response.data[0]["name"] == SUBCATEGORY_NAME_1
    assert response.data[0]["slug"] == SUBCATEGORY_SLUG_1


@pytest.mark.django_db
def test_get_subcategory_by_id(client, categories, subcategories):
    response = client.get(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk})
    )

    assert response.status_code == 200
    assert response.data["name"] == SUBCATEGORY_NAME_1
    assert response.data["slug"] == SUBCATEGORY_SLUG_1
    assert response.data["parent_category"] == categories[0].id


@pytest.mark.django_db
def test_create_subcategory(auth_admin, categories):
    payload = {"name": TEST_NAME, "parent_category": categories[0].id}
    response = auth_admin.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 201
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_create_subcategory_fail_if_not_admin(auth_client, categories):
    payload = {"name": TEST_NAME, "parent_category": categories[0].id}
    response = auth_client.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_subcategory_fail_if_not_authenticated(client, categories):
    payload = {"name": TEST_NAME, "parent_category": categories[0].id}
    response = client.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_subcategory_fail_no_name(auth_admin, categories):
    payload = {"parent_category": categories[0].id}
    response = auth_admin.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"


@pytest.mark.django_db
def test_create_subcategory_fail_slug_validation(auth_admin, categories):
    payload = {
        "name": TEST_NAME,
        "slug": INVALID_SLUG,
        "parent_category": categories[0].id,
    }
    response = auth_admin.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_create_subcategory_fail_no_parent_category(auth_admin):
    payload = {"name": TEST_NAME}
    response = auth_admin.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "parent_category"


@pytest.mark.django_db
def test_create_subcategory_fail_parent_category_validation(auth_admin):
    payload = {"name": TEST_NAME, "parent_category": INVALID_ID}
    response = auth_admin.post(reverse("api:subcategory-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "parent_category"


@pytest.mark.django_db
def test_edit_subcategory_name(auth_admin, subcategories):
    payload = {"name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == subcategories[0].slug


@pytest.mark.django_db
def test_edit_subcategory_slug(auth_admin, subcategories):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == subcategories[0].name
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_edit_subcategory_parent_category(auth_admin, categories, subcategories):
    payload = {"parent_category": categories[2].pk}
    response = auth_admin.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == subcategories[0].name
    assert response.data["slug"] == subcategories[0].slug
    assert response.data["parent_category"] == categories[2].pk


@pytest.mark.django_db
def test_edit_subcategory_fail_if_not_admin(auth_client, subcategories):
    payload = {"name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_subcategory_fail_if_not_authenticated(client, subcategories):
    payload = {"name": TEST_NAME}
    response = client.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_subcategory_fail_slug_validation(auth_admin, subcategories):
    payload = {"slug": INVALID_SLUG}
    response = auth_admin.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_edit_subcategory_fail_parent_category_validation(auth_admin, subcategories):
    payload = {"parent_category": INVALID_ID}
    response = auth_admin.patch(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "parent_category"


@pytest.mark.django_db
def test_delete_subcategory(auth_admin, subcategories):
    response = auth_admin.delete(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk})
    )

    assert response.status_code == 200
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_subcategory_fail_if_not_admin(auth_client, subcategories):
    response = auth_client.delete(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk})
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_delete_subcategory_fail_if_not_authenticated(client, subcategories):
    response = client.delete(
        reverse("api:subcategory-detail", kwargs={"pk": subcategories[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
