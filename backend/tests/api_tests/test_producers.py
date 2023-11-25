import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from products.models import Producer
from tests.fixtures import (
    INVALID_SLUG,
    INVALID_SLUG_MESSAGE,
    PRODUCER_ADDRESS_1,
    PRODUCER_NAME_1,
    PRODUCER_SLUG_1,
    TEST_ADDRESS,
    TEST_NAME,
    TEST_SLUG,
)


@pytest.mark.django_db
def test_get_producer_list(client, producers):
    response = client.get(reverse("api:producer-list"))

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["name"] == PRODUCER_NAME_1
    assert response.data[0]["slug"] == PRODUCER_SLUG_1
    assert response.data[0]["producer_type"] == Producer.COMPANY
    assert response.data[0]["address"] == PRODUCER_ADDRESS_1


@pytest.mark.django_db
def test_get_producer_by_id(client, producers):
    response = client.get(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk})
    )

    assert response.status_code == 200
    assert response.data["name"] == PRODUCER_NAME_1
    assert response.data["slug"] == PRODUCER_SLUG_1
    assert response.data["producer_type"] == Producer.COMPANY
    assert response.data["address"] == PRODUCER_ADDRESS_1


@pytest.mark.django_db
def test_create_producer(auth_admin):
    payload = {"name": TEST_NAME, "address": TEST_ADDRESS}
    response = auth_admin.post(reverse("api:producer-list"), payload)

    assert response.status_code == 201
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == TEST_SLUG
    assert response.data["producer_type"] == Producer.COMPANY
    assert response.data["address"] == TEST_ADDRESS


@pytest.mark.django_db
def test_create_producer_fail_if_not_admin(auth_client):
    payload = {"name": TEST_NAME, "address": TEST_ADDRESS}
    response = auth_client.post(reverse("api:producer-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_producer_fail_if_not_authenticated(client):
    payload = {"name": TEST_NAME, "address": TEST_ADDRESS}
    response = client.post(reverse("api:producer-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_producer_fail_name_validation(auth_admin):
    payload = {
        "slug": TEST_SLUG,
        "producer_type": Producer.COMPANY,
        "address": TEST_ADDRESS,
    }
    response = auth_admin.post(reverse("api:producer-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"


@pytest.mark.django_db
def test_create_producer_fail_slug_validation(auth_admin):
    payload = {
        "name": TEST_NAME,
        "slug": INVALID_SLUG,
        "producer_type": Producer.COMPANY,
        "address": TEST_ADDRESS,
    }
    response = auth_admin.post(reverse("api:producer-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_create_producer_fail_address_validation(auth_admin):
    payload = {"name": TEST_NAME}
    response = auth_admin.post(reverse("api:producer-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "address"


@pytest.mark.django_db
def test_edit_producer_name(auth_admin, producers):
    payload = {"name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == TEST_NAME
    assert response.data["slug"] == producers[0].slug
    assert response.data["producer_type"] == producers[0].producer_type
    assert response.data["address"] == producers[0].address


@pytest.mark.django_db
def test_edit_producer_slug(auth_admin, producers):
    payload = {"slug": TEST_SLUG}
    response = auth_admin.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == producers[0].name
    assert response.data["slug"] == TEST_SLUG
    assert response.data["producer_type"] == producers[0].producer_type
    assert response.data["address"] == producers[0].address


@pytest.mark.django_db
def test_edit_producer_type(auth_admin, producers):
    payload = {"producer_type": Producer.ENTREPRENEUR}
    response = auth_admin.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == producers[0].name
    assert response.data["slug"] == producers[0].slug
    assert response.data["producer_type"] == Producer.ENTREPRENEUR
    assert response.data["address"] == producers[0].address


@pytest.mark.django_db
def test_edit_producer_address(auth_admin, producers):
    payload = {"address": TEST_ADDRESS}
    response = auth_admin.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 200
    assert response.data["name"] == producers[0].name
    assert response.data["slug"] == producers[0].slug
    assert response.data["producer_type"] == producers[0].producer_type
    assert response.data["address"] == TEST_ADDRESS


@pytest.mark.django_db
def test_edit_producer_fail_if_not_admin(auth_client, producers):
    payload = {"name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_producer_fail_if_not_authenticated(client, producers):
    payload = {"name": TEST_NAME}
    response = client.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_producer_fail_slug_validation(auth_admin, producers):
    payload = {"slug": INVALID_SLUG}
    response = auth_admin.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["attr"] == "slug"
    assert response.data["errors"][0]["detail"] == INVALID_SLUG_MESSAGE


@pytest.mark.django_db
def test_edit_producer_fail_type_validation(auth_admin, producers):
    payload = {"producer_type": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "producer_type"


@pytest.mark.django_db
def test_delete_producer(auth_admin, producers):
    response = auth_admin.delete(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk})
    )

    assert response.status_code == 200
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_producer_fail_if_not_admin(auth_client, producers):
    response = auth_client.delete(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk})
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_delete_producer_fail_if_not_authenticated(client, producers):
    response = client.delete(
        reverse("api:producer-detail", kwargs={"pk": producers[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
