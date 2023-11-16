import pytest
from rest_framework.test import APIClient

client = APIClient()


@pytest.mark.django_db
def test_register_user():
    payload = {
        "username": "test_client",
        "email": "test_client@test.com",
        "password": "test_password",
    }

    response = client.post("/api/users/", payload)
    data = response.data

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["city"] == "Moscow"
    assert "password" not in data
