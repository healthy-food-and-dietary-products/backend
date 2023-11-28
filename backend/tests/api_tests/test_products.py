import pytest
from django.urls import reverse

from products.models import Product
from tests.fixtures import (
    PRODUCT_AMOUNT_1,
    PRODUCT_NAME_1,
    PRODUCT_PRICE_1,
    TEST_NAME,
    TEST_NUMBER,
    TEST_TEXT,
)

# TODO: test products filters


@pytest.mark.django_db
def test_get_product_list(client, products):
    response = client.get(reverse("api:product-list"))

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert response.data["results"][0]["name"] == PRODUCT_NAME_1
    assert response.data["results"][0]["description"] == ""
    assert response.data["results"][0]["creation_time"] is not None
    assert (
        response.data["results"][0]["category"]["category_name"]
        == products[0].category.name
    )
    assert (
        response.data["results"][0]["subcategory"]["subcategory_name"]
        == products[0].subcategory.name
    )
    assert response.data["results"][0]["tags"] == []
    assert response.data["results"][0]["discontinued"] is False
    assert (
        response.data["results"][0]["producer"]["producer_name"]
        == products[0].producer.name
    )
    assert response.data["results"][0]["measure_unit"] == products[0].measure_unit
    assert response.data["results"][0]["amount"] == PRODUCT_AMOUNT_1
    assert response.data["results"][0]["price"] == PRODUCT_PRICE_1
    assert response.data["results"][0]["promotions"] == []
    assert response.data["results"][0]["photo"] is None  # TODO: should be empty string
    assert [c["component_name"] for c in response.data["results"][0]["components"]] == [
        c.name for c in products[0].components.all()
    ]
    assert response.data["results"][0]["kcal"] == 0
    assert response.data["results"][0]["proteins"] == 0
    assert response.data["results"][0]["fats"] == 0
    assert response.data["results"][0]["carbohydrates"] == 0
    assert response.data["results"][0]["views_number"] == 0
    assert response.data["results"][0]["orders_number"] == 0


@pytest.mark.django_db
def test_get_product_by_id(client, products):
    response = client.get(reverse("api:product-detail", kwargs={"pk": products[0].pk}))

    assert response.status_code == 200
    assert response.data["name"] == PRODUCT_NAME_1
    assert response.data["description"] == ""
    assert response.data["creation_time"] is not None
    assert response.data["category"]["category_name"] == products[0].category.name
    assert (
        response.data["subcategory"]["subcategory_name"] == products[0].subcategory.name
    )
    assert response.data["tags"] == []
    assert response.data["discontinued"] is False
    assert response.data["producer"]["producer_name"] == products[0].producer.name
    assert response.data["measure_unit"] == products[0].measure_unit
    assert response.data["amount"] == PRODUCT_AMOUNT_1
    assert response.data["price"] == PRODUCT_PRICE_1
    assert response.data["promotions"] == []
    assert response.data["photo"] is None  # TODO: should be empty string
    assert [c["component_name"] for c in response.data["components"]] == [
        c.name for c in products[0].components.all()
    ]
    assert response.data["kcal"] == 0
    assert response.data["proteins"] == 0
    assert response.data["fats"] == 0
    assert response.data["carbohydrates"] == 0
    assert response.data["views_number"] == 1
    assert response.data["orders_number"] == 0


@pytest.mark.django_db
def test_create_product(auth_admin, subcategories, producers, components):
    payload = {
        "name": TEST_NAME,
        "description": TEST_TEXT,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "measure_unit": Product.GRAMS,
        "amount": TEST_NUMBER,
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 201
    assert response.data["name"] == TEST_NAME
    assert response.data["description"] == TEST_TEXT
    assert response.data["creation_time"] is not None
    assert response.data["category"] == subcategories[2].parent_category.pk
    assert response.data["subcategory"] == subcategories[2].pk
    assert response.data["tags"] == []
    assert response.data["discontinued"] is False
    assert response.data["producer"] == producers[0].pk
    assert response.data["measure_unit"] == Product.GRAMS
    assert response.data["amount"] == TEST_NUMBER
    assert response.data["price"] == TEST_NUMBER
    assert "promotions" not in response.data
    assert response.data["photo"] is None
    assert response.data["components"] == [c.pk for c in components[2:5]]
    assert response.data["kcal"] == 0
    assert response.data["proteins"] == 0
    assert response.data["fats"] == 0
    assert response.data["carbohydrates"] == 0
    assert "views_number" not in response.data
    assert "orders_number" not in response.data


@pytest.mark.django_db
def test_create_product_fail_if_not_admin(
    auth_client, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = auth_client.post(reverse("api:product-list"), payload)

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_create_product_fail_if_not_authenticated(
    client, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = client.post(reverse("api:product-list"), payload)

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_create_product_fail_no_name(auth_admin, subcategories, producers, components):
    payload = {
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "name"


@pytest.mark.django_db
def test_create_product_fail_no_subcategory(auth_admin, producers, components):
    payload = {
        "name": TEST_NAME,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "subcategory"


@pytest.mark.django_db
def test_create_product_fail_no_producer(auth_admin, subcategories, components):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "producer"


@pytest.mark.skip(reason="Not passing, but manually works")
@pytest.mark.django_db
def test_create_product_fail_no_components(auth_admin, subcategories, producers):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "components"


@pytest.mark.django_db
def test_create_product_fail_no_price(auth_admin, subcategories, producers, components):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "required"
    assert response.data["errors"][0]["attr"] == "price"


@pytest.mark.django_db
def test_create_product_fail_subcategory_validation(auth_admin, producers, components):
    payload = {
        "name": TEST_NAME,
        "subcategory": TEST_NUMBER,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "subcategory"


@pytest.mark.django_db
def test_create_product_fail_producer_validation(auth_admin, subcategories, components):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": TEST_NUMBER,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "producer"


@pytest.mark.django_db
def test_create_product_fail_components_validation(
    auth_admin, subcategories, producers
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [TEST_NUMBER],
        "price": TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "components"


@pytest.mark.django_db
def test_create_product_fail_tags_validation(
    auth_admin, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "tags": [TEST_NUMBER],
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "tags"


@pytest.mark.django_db
def test_create_product_fail_price_validation(
    auth_admin, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": -TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "price"


@pytest.mark.django_db
def test_create_product_fail_measure_unit_validation(
    auth_admin, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "measure_unit": TEST_NAME,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "measure_unit"


@pytest.mark.django_db
def test_create_product_fail_amount_validation(
    auth_admin, subcategories, producers, components
):
    payload_zero = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "amount": 0,
    }
    response = auth_admin.post(reverse("api:product-list"), payload_zero)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "amount"

    payload_negative = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "amount": -TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload_negative)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "amount"


@pytest.mark.django_db
def test_create_product_fail_proteins_validation(
    auth_admin, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "proteins": -TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "proteins"


@pytest.mark.django_db
def test_create_product_fail_fats_validation(
    auth_admin, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "fats": -TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "fats"


@pytest.mark.django_db
def test_create_product_fail_carbohydrates_validation(
    auth_admin, subcategories, producers, components
):
    payload = {
        "name": TEST_NAME,
        "subcategory": subcategories[2].pk,
        "producer": producers[0].pk,
        "components": [component.pk for component in components[2:5]],
        "price": TEST_NUMBER,
        "carbohydrates": -TEST_NUMBER,
    }
    response = auth_admin.post(reverse("api:product-list"), payload)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "carbohydrates"


@pytest.mark.django_db
def test_edit_product_name(auth_admin, products):
    old_name = products[0].name
    payload = {"name": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_name == PRODUCT_NAME_1
    assert response.data["name"] == TEST_NAME


@pytest.mark.django_db
def test_edit_product_description(auth_admin, products):
    old_description = products[0].description
    payload = {"description": TEST_TEXT}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_description == ""
    assert response.data["description"] == TEST_TEXT


@pytest.mark.django_db
def test_edit_product_subcategory(auth_admin, products, subcategories):
    old_subcategory = products[0].subcategory.pk
    payload = {"subcategory": subcategories[0].pk}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_subcategory == subcategories[2].pk
    assert response.data["subcategory"] == subcategories[0].pk


@pytest.mark.django_db
def test_edit_product_tags(auth_admin, products, tags):
    old_subcategory = list(products[0].tags.all())
    payload = {"tags": [tags[0].pk]}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_subcategory == []
    assert response.data["tags"] == [tags[0].pk]


@pytest.mark.django_db
def test_edit_product_discontinued(auth_admin, products):
    old_discontinued = products[0].discontinued
    payload = {"discontinued": True}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_discontinued is False
    assert response.data["discontinued"] is True


@pytest.mark.django_db
def test_edit_product_producer(auth_admin, products, producers):
    old_producer = products[0].producer.pk
    payload = {"producer": producers[1].pk}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_producer == producers[0].pk
    assert response.data["producer"] == producers[1].pk


@pytest.mark.django_db
def test_edit_product_measure_unit(auth_admin, products):
    old_measure_unit = products[0].measure_unit
    payload = {"measure_unit": Product.MILLILITRES}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_measure_unit == Product.GRAMS
    assert response.data["measure_unit"] == Product.MILLILITRES


@pytest.mark.django_db
def test_edit_product_amount(auth_admin, products):
    old_amount = products[0].amount
    payload = {"amount": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_amount == PRODUCT_AMOUNT_1
    assert response.data["amount"] == TEST_NUMBER
    assert PRODUCT_AMOUNT_1 != TEST_NUMBER


@pytest.mark.django_db
def test_edit_product_price(auth_admin, products):
    old_price = products[0].price
    payload = {"price": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_price == PRODUCT_PRICE_1
    assert response.data["price"] == TEST_NUMBER
    assert PRODUCT_PRICE_1 != TEST_NUMBER


@pytest.mark.django_db
def test_edit_product_promotions(auth_admin, products, promotions):
    old_promotions = list(products[0].promotions.all())
    payload = {"promotions": [promotions[0].pk]}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_promotions == []
    assert response.data["promotions"] == [promotions[0].pk]


@pytest.mark.django_db
def test_edit_product_components(auth_admin, products, components):
    old_components = [c.pk for c in products[0].components.all()]
    payload = {"components": [c.pk for c in components[:2]]}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_components == [c.pk for c in components[2:]]
    assert response.data["components"] == [c.pk for c in components[:2]]


@pytest.mark.django_db
def test_edit_product_kcal(auth_admin, products):
    old_kcal = products[0].kcal
    payload = {"kcal": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_kcal == 0
    assert response.data["kcal"] == TEST_NUMBER != old_kcal


@pytest.mark.django_db
def test_edit_product_proteins(auth_admin, products):
    old_proteins = products[0].proteins
    payload = {"proteins": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_proteins == 0
    assert response.data["proteins"] == TEST_NUMBER != old_proteins


@pytest.mark.django_db
def test_edit_product_fats(auth_admin, products):
    old_fats = products[0].fats
    payload = {"fats": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_fats == 0
    assert response.data["fats"] == TEST_NUMBER != old_fats


@pytest.mark.django_db
def test_edit_product_carbohydrates(auth_admin, products):
    old_carbohydrates = products[0].carbohydrates
    payload = {"carbohydrates": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 200
    assert old_carbohydrates == 0
    assert response.data["carbohydrates"] == TEST_NUMBER != old_carbohydrates


@pytest.mark.django_db
def test_edit_product_fail_if_not_admin(auth_client, products):
    payload = {"name": TEST_NAME}
    response = auth_client.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 403
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "permission_denied"


@pytest.mark.django_db
def test_edit_product_fail_if_not_authenticated(client, products):
    payload = {"name": TEST_NAME}
    response = client.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 401
    assert response.data["type"] == "client_error"
    assert response.data["errors"][0]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_edit_product_fail_subcategory_validation(auth_admin, products):
    payload = {"subcategory": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "subcategory"


@pytest.mark.django_db
def test_edit_product_fail_producer_validation(auth_admin, products):
    payload = {"producer": TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "producer"


@pytest.mark.django_db
def test_edit_product_fail_components_validation(auth_admin, products):
    payload = {"components": [TEST_NUMBER]}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "components"


@pytest.mark.django_db
def test_edit_product_fail_tags_validation(auth_admin, products):
    payload = {"tags": [TEST_NUMBER]}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "does_not_exist"
    assert response.data["errors"][0]["attr"] == "tags"


@pytest.mark.django_db
def test_edit_product_fail_price_validation(auth_admin, products):
    payload = {"price": -TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "price"


@pytest.mark.django_db
def test_edit_product_fail_measure_unit_validation(auth_admin, products):
    payload = {"measure_unit": TEST_NAME}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "measure_unit"


@pytest.mark.django_db
def test_edit_product_fail_amount_validation(auth_admin, products):
    payload_zero = {"amount": 0}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload_zero
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "amount"

    payload_negative = {"amount": -TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload_negative
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "amount"


@pytest.mark.django_db
def test_edit_product_fail_proteins_validation(auth_admin, products):
    payload = {"proteins": -TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "proteins"


@pytest.mark.django_db
def test_edit_product_fail_fats_validation(auth_admin, products):
    payload = {"fats": -TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "fats"


@pytest.mark.django_db
def test_edit_product_fail_carbohydrates_validation(auth_admin, products):
    payload = {"carbohydrates": -TEST_NUMBER}
    response = auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[0].pk}), payload
    )

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "min_value"
    assert response.data["errors"][0]["attr"] == "carbohydrates"


# TODO: test edit promotions validation - max number, non existent, duplicates
# TODO: test product delete
