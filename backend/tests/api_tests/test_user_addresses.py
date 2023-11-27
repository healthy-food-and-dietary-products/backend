import pytest
from django.urls import reverse

from tests.fixtures import ADDRESS1, ADDRESS2


@pytest.mark.django_db
def test_patch_user_addresses(user, auth_client):
    payload = {
        "addresses": [
            {"address": ADDRESS1, "priority_address": "true"},
            {"address": ADDRESS2, "priority_address": "false"},
        ],
    }
    response = auth_client.patch(reverse("api:user-me"), payload, format="json")

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert len(response.data["addresses"]) == 2
    assert response.data["addresses"][0]["address"] == ADDRESS1
    assert response.data["addresses"][1]["address"] == ADDRESS2


@pytest.mark.django_db
def test_patch_user_addresses_default_priority(user, auth_client):
    payload = {"addresses": [{"address": ADDRESS1}, {"address": ADDRESS2}]}
    response = auth_client.patch(reverse("api:user-me"), payload, format="json")

    assert response.status_code == 200
    assert len(response.data["addresses"]) == 2
    assert response.data["addresses"][0]["priority_address"] is False
    assert response.data["addresses"][1]["priority_address"] is False


@pytest.mark.django_db
def test_patch_user_addresses_priority_fail(user, auth_client):
    payload = {
        "addresses": [
            {"address": ADDRESS1, "priority_address": "true"},
            {"address": ADDRESS2, "priority_address": "true"},
        ],
    }
    response = auth_client.patch(reverse("api:user-me"), payload, format="json")

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert (
        response.data["errors"][0]["detail"]
        == "Разрешен только один приоритетный адрес."
    )


@pytest.mark.django_db
def test_patch_user_same_addresses_save_as_one(user, auth_client):
    payload = {
        "addresses": [
            {"address": ADDRESS1, "priority_address": "true"},
            {"address": ADDRESS1, "priority_address": "true"},
        ],
    }
    response = auth_client.patch(reverse("api:user-me"), payload, format="json")

    assert response.status_code == 200
    assert len(response.data["addresses"]) == 1
    assert response.data["addresses"][0]["address"] == ADDRESS1


@pytest.mark.django_db
def test_patch_user_addresses_anonymous_fail(user, client):
    payload = {"addresses": [{"address": ADDRESS1, "priority_address": "true"}]}
    response = client.patch(reverse("api:user-me"), payload, format="json")

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_patch_user_addresses_deletion(user, auth_client):
    payload = {
        "addresses": [
            {"address": ADDRESS1, "priority_address": "true"},
            {"address": ADDRESS2, "priority_address": "false"},
        ],
    }
    response_create = auth_client.patch(reverse("api:user-me"), payload, format="json")

    assert response_create.status_code == 200
    assert len(response_create.data["addresses"]) == 2

    response_delete = auth_client.patch(
        reverse("api:user-me"), {"addresses": []}, format="json"
    )

    assert response_delete.status_code == 200
    assert len(response_delete.data["addresses"]) == 0
