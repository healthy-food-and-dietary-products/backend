import pytest
from tests.conftest import CITY, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, USERNAME


@pytest.mark.django_db
def test_register_user(client):
    payload = {"username": USERNAME, "email": EMAIL, "password": PASSWORD}
    response = client.post("/api/users/", payload)

    assert response.status_code == 201
    assert response.data["username"] == payload["username"]
    assert response.data["email"] == payload["email"]
    assert response.data["city"] == CITY
    assert "password" not in response.data


@pytest.mark.django_db
def test_register_user_validation_fail(client):
    payload = [
        {"username": USERNAME, "email": EMAIL},
        {"username": USERNAME, "password": PASSWORD},
        {"email": EMAIL, "password": PASSWORD},
    ]
    for field in payload:
        response = client.post("/api/users/", field)

        assert response.status_code == 200
        assert response.data["type"] == "validation_error"
        assert response.data["errors"][0]["code"] == "required"


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
def test_logout_user(auth_client):
    response = auth_client.post("/api/token/logout/")

    assert response.status_code == 204


@pytest.mark.django_db
def test_get_me(user, auth_client):
    response = auth_client.get("/api/users/me/")

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["city"] == user.city
    assert "password" not in response.data


@pytest.mark.django_db
def test_patch_me(user, auth_client):
    payload = {"first_name": FIRST_NAME, "last_name": LAST_NAME}
    response = auth_client.patch("/api/users/me/", payload)
    # user.refresh_from_db() seems it is not necessary

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["first_name"] == user.first_name == FIRST_NAME
    assert response.data["last_name"] == user.last_name == LAST_NAME


@pytest.mark.django_db
def test_patch_me_anonymous_fail(client):
    payload = {"first_name": FIRST_NAME, "last_name": LAST_NAME}
    response = client.patch("/api/users/me/", payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_delete_me(auth_client, user):
    response = auth_client.delete("/api/users/me/")

    assert response.status_code == 200
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["Success"] == "This object was successfully deleted"


@pytest.mark.django_db
def test_delete_me_anonymous_fail(client):
    response = client.delete("/api/users/me/")

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
