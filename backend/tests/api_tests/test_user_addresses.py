import pytest
from tests.conftest import ADDRESS1

from users.models import Address


@pytest.mark.django_db
def test_patch_user_addresses(user, auth_client):
    payload = dict(addresses=[dict(address=ADDRESS1)])
    # payload = {
    #     "addresses": [
    #         {"address": ADDRESS1, "priority_address": "true"},
    #         {"address": ADDRESS2, "priority_address": "false"},
    #     ],
    #     "first_name": FIRST_NAME,
    # }
    response = auth_client.patch("/api/users/me/", payload)
    print(response.data)
    print(Address.objects.all())

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    # assert response.data["addresses"][0]["address"] == ADDRESS1
