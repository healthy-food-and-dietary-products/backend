import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from tests.fixtures import (
    INVALID_SLUG,
    INVALID_SLUG_MESSAGE,
    TAG_NAME_1,
    TAG_SLUG_1,
    TEST_NAME,
    TEST_SLUG,
)


@pytest.mark.django_db
def test_get_tag_list(client, tags):
    response = client.get(reverse("api:tag-list"))

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["name"] == TAG_NAME_1
    assert response.data[0]["slug"] == TAG_SLUG_1


@pytest.mark.django_db
def test_get_tag_by_id(client, tags):
    response = client.get(reverse("api:tag-detail", kwargs={"pk": tags[0].pk}))

    assert response.status_code == 200
    assert response.data["name"] == TAG_NAME_1
    assert response.data["slug"] == TAG_SLUG_1


@pytest.mark.django_db
def test_create_tag(auth_admin):
    payload = {"name": TEST_NAME}
    response = auth_admin.post(reverse("api:tag-list"), payload)

    assert response.status_code == 201
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_create_tag_fail_if_not_admin(auth_client):
    payload = {"name": TEST_NAME}
    response = auth_client.post(reverse("api:tag-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_tag_fail_if_not_authenticated(client):
    payload = {"name": TEST_NAME}
    response = client.post(reverse("api:tag-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_tag_fail_no_name(auth_admin):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.post(reverse("api:tag-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"


@pytest.mark.django_db
def test_create_tag_fail_slug_validation(auth_admin):
    payload = {"name": TEST_NAME, "slug": INVALID_SLUG}
    response = auth_admin.post(reverse("api:tag-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_edit_tag_name(auth_admin, tags):
    payload = {"name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:tag-detail", kwargs={"pk": tags[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == tags[0].slug


@pytest.mark.django_db
def test_edit_tag_slug(auth_admin, tags):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.patch(
        reverse("api:tag-detail", kwargs={"pk": tags[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == tags[0].name
    assert response.data["slug"] == TEST_SLUG


@pytest.mark.django_db
def test_edit_tag_fail_if_not_admin(auth_client, tags):
    payload = {"name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:tag-detail", kwargs={"pk": tags[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_tag_fail_if_not_authenticated(client, tags):
    payload = {"name": TEST_NAME}
    response = client.patch(
        reverse("api:tag-detail", kwargs={"pk": tags[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_tag_fail_slug_validation(auth_admin, tags):
    payload = {"slug": INVALID_SLUG}
    response = auth_admin.patch(
        reverse("api:tag-detail", kwargs={"pk": tags[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_delete_tag(auth_admin, tags):
    response = auth_admin.delete(reverse("api:tag-detail", kwargs={"pk": tags[0].pk}))

    assert response.status_code == 200
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_tag_fail_if_not_admin(auth_client, tags):
    response = auth_client.delete(reverse("api:tag-detail", kwargs={"pk": tags[0].pk}))

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_delete_tag_fail_if_not_authenticated(client, tags):
    response = client.delete(reverse("api:tag-detail", kwargs={"pk": tags[0].pk}))

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
