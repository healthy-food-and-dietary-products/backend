import pytest
from tests.conftest import EMAIL, PASSWORD, USERNAME

CITY = "Moscow"


@pytest.mark.django_db
def test_register_user(client):
    payload = {"username": USERNAME, "email": EMAIL, "password": PASSWORD}
    response = client.post("/api/users/", payload)

    assert response.data["username"] == payload["username"]
    assert response.data["email"] == payload["email"]
    assert response.data["city"] == CITY
    assert "password" not in response.data


@pytest.mark.django_db
def test_login_user(user, client):
    response = client.post("/api/token/login/", dict(email=EMAIL, password=PASSWORD))

    assert response.status_code == 200
    assert "auth_token" in response.data
    assert len(response.data["auth_token"]) == 40


@pytest.mark.django_db
def test_login_user_fail(client):
    response = client.post("/api/token/login/", dict(email=EMAIL, password=PASSWORD))

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_credentials"


@pytest.mark.django_db
def test_get_me(user, auth_client):
    response = auth_client.get("/api/users/me/")

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["city"] == user.city
    assert "password" not in response.data
