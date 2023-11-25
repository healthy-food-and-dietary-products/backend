import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from tests.fixtures import (
    COMPONENT_NAME_1,
    COMPONENT_SLUG_1,
    INVALID_SLUG,
    INVALID_SLUG_MESSAGE,
    TEST_NAME,
    TEST_SLUG,
)


@pytest.mark.django_db
def test_get_component_list(client, components):
    response = client.get(reverse("api:component-list"))

    assert response.status_code == 200
    assert len(response.data) == 8
    assert response.data[0]["name"] == COMPONENT_NAME_1
    assert response.data[0]["slug"] == COMPONENT_SLUG_1


@pytest.mark.django_db
def test_get_component_by_id(client, components):
    response = client.get(
        reverse("api:component-detail", kwargs={"pk": components[0].pk})
    )

    assert response.status_code == 200
    assert response.data["name"] == COMPONENT_NAME_1
    assert response.data["slug"] == COMPONENT_SLUG_1


@pytest.mark.django_db
def test_create_component(auth_admin):
    payload = {"name": TEST_NAME}
    response = auth_admin.post(reverse("api:component-list"), payload)

    assert response.status_code == 201
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_create_component_fail_if_not_admin(auth_client):
    payload = {"name": TEST_NAME}
    response = auth_client.post(reverse("api:component-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_component_fail_if_not_authenticated(client):
    payload = {"name": TEST_NAME}
    response = client.post(reverse("api:component-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_component_fail_name_validation(auth_admin):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.post(reverse("api:component-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"


@pytest.mark.django_db
def test_create_component_fail_slug_validation(auth_admin):
    payload = {"name": TEST_NAME, "slug": INVALID_SLUG}
    response = auth_admin.post(reverse("api:component-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_edit_component_name(auth_admin, components):
    payload = {"name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:component-detail", kwargs={"pk": components[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == components[0].slug


@pytest.mark.django_db
def test_edit_component_slug(auth_admin, components):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.patch(
        reverse("api:component-detail", kwargs={"pk": components[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == components[0].name
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_edit_component_fail_if_not_admin(auth_client, components):
    payload = {"name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:component-detail", kwargs={"pk": components[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_component_fail_if_not_authenticated(client, components):
    payload = {"name": TEST_NAME}
    response = client.patch(
        reverse("api:component-detail", kwargs={"pk": components[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_component_fail_slug_validation(auth_admin, components):
    payload = {"slug": INVALID_SLUG}
    response = auth_admin.patch(
        reverse("api:component-detail", kwargs={"pk": components[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_delete_component(auth_admin, components):
    response = auth_admin.delete(
        reverse("api:component-detail", kwargs={"pk": components[0].pk})
    )

    assert response.status_code == 200
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_component_fail_if_not_admin(auth_client, components):
    response = auth_client.delete(
        reverse("api:component-detail", kwargs={"pk": components[0].pk})
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_delete_component_fail_if_not_authenticated(client, components):
    response = client.delete(
        reverse("api:component-detail", kwargs={"pk": components[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
