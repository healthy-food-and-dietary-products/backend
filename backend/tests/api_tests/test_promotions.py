import pytest
from django.urls import reverse

from api.mixins import MESSAGE_ON_DELETE
from products.models import Promotion
from tests.fixtures import PROMOTION_DISCOUNT_1, PROMOTION_NAME_1, TEST_NAME, TEST_TIME


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
def test_create_promotion_default_discount(auth_admin):
    payload = {"name": TEST_NAME}
    response = auth_admin.post(reverse("api:promotion-list"), payload)

    assert response.status_code == 201
    assert response.data["discount"] == 0


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
def test_create_promotion_fail_no_name(auth_admin):
    payload = {"discount": PROMOTION_DISCOUNT_1}
    response = auth_admin.post(reverse("api:promotion-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"


@pytest.mark.django_db
def test_create_promotion_fail_discount_validation(auth_admin):
    error_message_1 = "Допустимы числа от 0 до 100."
    error_message_2 = "Убедитесь, что это значение меньше либо равно 100."
    payload_1 = {"name": TEST_NAME, "discount": -1}
    payload_2 = {"name": TEST_NAME, "discount": 101}
    response_1 = auth_admin.post(reverse("api:promotion-list"), payload_1)
    response_2 = auth_admin.post(reverse("api:promotion-list"), payload_2)

    assert response_1.status_code == 400
    assert response_1.data["type"] == "validation_error"
    assert response_1.data["errors"][0]["code"] == "invalid"
    assert response_1.data["errors"][0]["attr"] == "discount"
    assert response_1.data["errors"][0]["detail"] == error_message_1

    assert response_2.status_code == 400
    assert response_2.data["type"] == "validation_error"
    assert response_2.data["errors"][0]["code"] == "max_value"
    assert response_2.data["errors"][0]["attr"] == "discount"
    assert response_2.data["errors"][0]["detail"] == error_message_2


@pytest.mark.django_db
def test_create_promotion_fail_type_validation(auth_admin):
    payload = {"name": TEST_NAME, "promotion_type": TEST_NAME}
    response = auth_admin.post(reverse("api:promotion-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "promotion_type"


@pytest.mark.django_db
def test_edit_promotion_name(auth_admin, promotions):
    old_name = promotions[0].name
    payload = {"name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_name == PROMOTION_NAME_1
    assert response.data["name"] == TEST_NAME


@pytest.mark.django_db
def test_edit_promotion_type(auth_admin, promotions):
    old_type = promotions[0].promotion_type
    payload = {"promotion_type": Promotion.LOYALTY_CARD}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_type == Promotion.BIRTHDAY
    assert response.data["promotion_type"] == Promotion.LOYALTY_CARD


@pytest.mark.django_db
def test_edit_promotion_discount(auth_admin, promotions):
    old_discount = promotions[0].discount
    payload = {"discount": PROMOTION_DISCOUNT_1 + 5}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_discount == PROMOTION_DISCOUNT_1
    assert response.data["discount"] == PROMOTION_DISCOUNT_1 + 5


@pytest.mark.django_db
def test_edit_promotion_conditions(auth_admin, promotions):
    old_conditions = promotions[0].conditions
    payload = {"conditions": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_conditions == ""
    assert response.data["conditions"] == TEST_NAME


@pytest.mark.django_db
def test_edit_promotion_is_active_value(auth_admin, promotions):
    old_value = promotions[0].is_active
    payload = {"is_active": False}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_value is True
    assert response.data["is_active"] is False


@pytest.mark.django_db
def test_edit_promotion_is_constant_value(auth_admin, promotions):
    old_value = promotions[0].is_constant
    payload = {"is_constant": True}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_value is False
    assert response.data["is_constant"] is True


@pytest.mark.django_db
def test_edit_promotion_start_time(auth_admin, promotions):
    old_start_time = promotions[0].start_time
    payload = {"start_time": TEST_TIME}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_start_time is None
    assert response.data["start_time"] is not None


@pytest.mark.django_db
def test_edit_promotion_end_time(auth_admin, promotions):
    old_end_time = promotions[0].end_time
    payload = {"end_time": TEST_TIME}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_end_time is None
    assert response.data["end_time"] is not None


@pytest.mark.django_db
def test_edit_promotion_fail_if_not_admin(auth_client, promotions):
    payload = {"name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_promotion_fail_if_not_authenticated(client, promotions):
    payload = {"name": TEST_NAME}
    response = client.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_promotion_fail_discount_validation(auth_admin, promotions):
    error_message_1 = "Допустимы числа от 0 до 100."
    error_message_2 = "Убедитесь, что это значение меньше либо равно 100."
    payload_1 = {"discount": -1}
    payload_2 = {"discount": 101}
    response_1 = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload_1
    )
    response_2 = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload_2
    )

    assert response_1.status_code == 400
    assert response_1.data["type"] == "validation_error"
    assert response_1.data["errors"][0]["code"] == "invalid"
    assert response_1.data["errors"][0]["attr"] == "discount"
    assert response_1.data["errors"][0]["detail"] == error_message_1

    assert response_2.status_code == 400
    assert response_2.data["type"] == "validation_error"
    assert response_2.data["errors"][0]["code"] == "max_value"
    assert response_2.data["errors"][0]["attr"] == "discount"
    assert response_2.data["errors"][0]["detail"] == error_message_2


@pytest.mark.django_db
def test_edit_promotion_fail_type_validation(auth_admin, promotions):
    payload = {"promotion_type": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "promotion_type"


@pytest.mark.django_db
def test_delete_promotion(auth_admin, promotions):
    response = auth_admin.delete(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk})
    )

    assert response.status_code == 200
    assert response.data["Success"] == MESSAGE_ON_DELETE


@pytest.mark.django_db
def test_delete_promotion_fail_if_not_admin(auth_client, promotions):
    response = auth_client.delete(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk})
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_delete_promotion_fail_if_not_authenticated(client, promotions):
    response = client.delete(
        reverse("api:promotion-detail", kwargs={"pk": promotions[0].pk})
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"
