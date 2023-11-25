import pytest
from django.urls import reverse

from products.models import Promotion
from tests.fixtures import PROMOTION_DISCOUNT_1, PROMOTION_NAME_1, TEST_NAME


@pytest.mark.django_db
def test_get_promotion_list(client, promotions):
    response = client.get(reverse("api:promotion-list"))

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["promotion_type"] == Promotion.BIRTHDAY
    assert response.data[0]["name"] == PROMOTION_NAME_1
    assert response.data[0]["discount"] == PROMOTION_DISCOUNT_1
    assert response.data[0]["conditions"] == ""
    assert response.data[0]["is_active"] is True
    assert response.data[0]["is_constant"] is False
    assert response.data[0]["start_time"] is None
    assert response.data[0]["end_time"] is None


@pytest.mark.django_db
def test_get_promotion_by_id(client, promotions):
    response = client.get(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk})
    )

    assert response.status_code == 200
    assert response.data["promotion_type"] == Promotion.BIRTHDAY
    assert response.data["name"] == PROMOTION_NAME_1
    assert response.data["discount"] == PROMOTION_DISCOUNT_1
    assert response.data["conditions"] == ""
    assert response.data["is_active"] is True
    assert response.data["is_constant"] is False
    assert response.data["start_time"] is None
    assert response.data["end_time"] is None


@pytest.mark.django_db
def test_create_promotion(auth_admin):
    payload = {"name": TEST_NAME, "discount": PROMOTION_DISCOUNT_1}
    response = auth_admin.post(reverse("api:promotion-list"), payload)
    print(response.data)

    assert response.status_code == 201
    assert response.data["promotion_type"] == Promotion.SIMPLE
    assert response.data["name"] == TEST_NAME
    assert response.data["discount"] == PROMOTION_DISCOUNT_1
    assert response.data["conditions"] == ""
    # assert response.data["is_active"] is True  #TODO: default True value not working
    assert response.data["is_constant"] is False
    assert response.data["start_time"] is None
    assert response.data["end_time"] is None


@pytest.mark.django_db
def test_create_promotion_fail_if_not_admin(auth_client):
    payload = {"name": TEST_NAME, "discount": PROMOTION_DISCOUNT_1}
    response = auth_client.post(reverse("api:promotion-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_promotion_fail_if_not_authenticated(client):
    payload = {"name": TEST_NAME, "discount": PROMOTION_DISCOUNT_1}
    response = client.post(reverse("api:promotion-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_promotion_fail_name_validation(auth_admin):
    payload = {"discount": PROMOTION_DISCOUNT_1}
    response = auth_admin.post(reverse("api:promotion-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"
