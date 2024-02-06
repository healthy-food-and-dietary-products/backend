import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework.fields import DateField

from api.mixins import MESSAGE_ON_DELETE
from tests.fixtures import (
    BIRTH_DATE,
    CITY,
    FIRST_NAME,
    LAST_NAME,
    PASSWORD,
    PHONE_NUMBER,
    USER,
    USER_EMAIL,
)
from users.models import (
    BIRTH_DATE_TOO_OLD_ERROR_MESSAGE,
    BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE,
    MAX_USER_AGE,
    MIN_USER_AGE,
    PHONE_NUMBER_ERROR,
)

BIRTH_DATE_FORMAT_ERROR_MESSAGE = DateField.default_error_messages["invalid"].format(
    format="DD.MM.YYYY"
)


@pytest.mark.django_db
def test_get_user_anonymous_fail(client):
    response = client.get(reverse("api:user-list"))

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_register_user(client):
    payload = {"username": USER, "email": USER_EMAIL, "password": PASSWORD}
    response = client.post(reverse("api:user-list"), payload)

    assert response.status_code == 201
    assert response.data["username"] == payload["username"]
    assert response.data["email"] == payload["email"]
    assert response.data["city"] == CITY
    assert "password" not in response.data


@pytest.mark.django_db
def test_register_user_validation_fail(client):
    payload = [
        {"username": USER, "email": USER_EMAIL},
        {"username": USER, "password": PASSWORD},
        {"email": USER_EMAIL, "password": PASSWORD},
    ]
    for field in payload:
        response = client.post(reverse("api:user-list"), field)

        assert response.status_code == 400
        assert response.data["type"] == "validation_error"
        assert response.data["errors"][0]["code"] == "required"


@pytest.mark.django_db
def test_login_user(user, client):
    response = client.post(
        reverse("api:login"), dict(email=USER_EMAIL, password=PASSWORD)
    )

    assert response.status_code == 200
    assert "auth_token" in response.data
    assert len(response.data["auth_token"]) == 40


@pytest.mark.django_db
def test_login_user_fail(client):
    response = client.post(
        reverse("api:login"), dict(email=USER_EMAIL, password=PASSWORD)
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_credentials"


@pytest.mark.django_db
def test_logout_user(auth_client):
    response = auth_client.post(reverse("api:logout"))

    assert response.status_code == 204


@pytest.mark.django_db
def test_get_me(user, auth_client):
    response = auth_client.get(reverse("api:user-me"))

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["city"] == user.city
    assert "password" not in response.data


@pytest.mark.django_db
def test_patch_me_first_last_names(user, auth_client):
    payload = {"first_name": FIRST_NAME, "last_name": LAST_NAME}
    response = auth_client.patch(reverse("api:user-me"), payload)

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["first_name"] == user.first_name == FIRST_NAME
    assert response.data["last_name"] == user.last_name == LAST_NAME


@pytest.mark.django_db
def test_patch_me_birth_date_post(user, auth_client):
    response_get = auth_client.get(reverse("api:user-me"))
    assert response_get.data["birth_date"] is None

    payload = {"birth_date": BIRTH_DATE}
    response_post = auth_client.patch(reverse("api:user-me"), payload)
    assert response_post.status_code == 200
    assert response_post.data["birth_date"] == BIRTH_DATE


@pytest.mark.django_db
def test_patch_me_too_young_birth_date(user, auth_client):
    response_get = auth_client.get(reverse("api:user-me"))
    assert response_get.data["birth_date"] is None

    date = (
        timezone.now().date()
        - relativedelta(years=MIN_USER_AGE)
        + relativedelta(days=1)
    )
    date = date.__format__("%d.%m.%Y")
    payload = {"birth_date": date}
    response = auth_client.patch(reverse("api:user-me"), payload)
    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["detail"] == BIRTH_DATE_TOO_YOUNG_ERROR_MESSAGE


@pytest.mark.django_db
def test_patch_me_too_old_birth_date(user, auth_client):
    response_get = auth_client.get(reverse("api:user-me"))
    assert response_get.data["birth_date"] is None

    date = (
        timezone.now().date()
        - relativedelta(years=MAX_USER_AGE)
        - relativedelta(days=1)
    )
    date = date.__format__("%d.%m.%Y")
    payload = {"birth_date": date}
    response = auth_client.patch(reverse("api:user-me"), payload)
    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["detail"] == BIRTH_DATE_TOO_OLD_ERROR_MESSAGE


@pytest.mark.django_db
def test_patch_me_birth_date_post_fail(user, auth_client):
    payload = {"birth_date": "01-01-2000"}
    response = auth_client.patch(reverse("api:user-me"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["detail"] == BIRTH_DATE_FORMAT_ERROR_MESSAGE


@pytest.mark.django_db
def test_patch_me_birth_date_set_null(user, auth_client):
    payload = {"birth_date": BIRTH_DATE}
    response_post = auth_client.patch(reverse("api:user-me"), payload)
    assert response_post.status_code == 200
    assert response_post.data["birth_date"] == BIRTH_DATE

    # pytest/unittest don't accept None (i.e. null) in payload and responds with
    # the error "TypeError: Cannot encode None for key 'birth_date' as POST data.
    # Did you mean to pass an empty string or omit the value?"
    # However, if we pass an empty string as payload, pytest will count it as null.
    # We also wanted to make a test for an empty string, to which our API responds
    # with code 400 (incorrect date format error), but pytest/unittest equates it
    # to None, so we cannot write such a test.
    payload_to_delete_birth_date = {"birth_date": ""}
    response_delete = auth_client.patch(
        reverse("api:user-me"), payload_to_delete_birth_date
    )
    assert response_delete.status_code == 200
    assert response_delete.data["birth_date"] is None


@pytest.mark.django_db
def test_patch_me_phone_number(user, auth_client):
    response_get = auth_client.get(reverse("api:user-me"))
    assert response_get.data["phone_number"] == ""

    payload = {"phone_number": PHONE_NUMBER}
    response_post = auth_client.patch(reverse("api:user-me"), payload)
    assert response_post.status_code == 200
    assert response_post.data["phone_number"] == user.phone_number == PHONE_NUMBER

    payload = {"phone_number": ""}
    response = auth_client.patch(reverse("api:user-me"), payload)
    assert response.status_code == 200
    assert response.data["phone_number"] == ""

    payload = {"phone_number": "4"}
    response = auth_client.patch(reverse("api:user-me"), payload)
    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid"
    assert response.data["errors"][0]["detail"] == PHONE_NUMBER_ERROR


@pytest.mark.django_db
def test_patch_me_anonymous_fail(client):
    payload = {"first_name": FIRST_NAME, "last_name": LAST_NAME}
    response = client.patch(reverse("api:user-me"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_delete_me(auth_client, user):
    response = auth_client.delete(reverse("api:user-me"))

    assert response.status_code == 200
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_me_anonymous_fail(client):
    response = client.delete(reverse("api:user-me"))

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
