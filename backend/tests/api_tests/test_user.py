import pytest
from tests.conftest import EMAIL, PASSWORD, USERNAME

CITY = "Moscow"


@pytest.mark.django_db
def test_register_user(client):
    payload = {"username": USERNAME, "email": EMAIL, "password": PASSWORD}
    response = client.post("/api/users/", payload)
    data = response.data

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["city"] == CITY
    assert "password" not in data


@pytest.mark.django_db
def test_login_user(user, client):
    response = client.post("/api/token/login/", dict(email=EMAIL, password=PASSWORD))
    data = response.data

    assert response.status_code == 200
    assert "auth_token" in data
    assert len(data["auth_token"]) == 40


@pytest.mark.django_db
def test_login_user_fail(client):
    response = client.post(
        "/api/token/login/",
        {"email": "test_client@test.com", "password": "test_password"},
    )
    data = response.data

    assert response.status_code == 400
    assert data["type"] == "validation_error"
    assert data["errors"][0]["code"] == "invalid_credentials"
