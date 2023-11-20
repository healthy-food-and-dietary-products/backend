import pytest
from tests.fixtures import ADDRESS1, ADDRESS2


@pytest.mark.django_db
def test_patch_user_addresses(user, auth_client):
    payload = {
        "addresses": [
            {"address": ADDRESS1, "priority_address": "true"},
            {"address": ADDRESS2, "priority_address": "false"},
        ],
    }
    response = auth_client.patch("/api/users/me/", payload, format="json")

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["addresses"][0]["address"] == ADDRESS1
    assert response.data["addresses"][1]["address"] == ADDRESS2
