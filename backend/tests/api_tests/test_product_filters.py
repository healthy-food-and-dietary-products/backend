import pytest
from django.urls import reverse

from tests.fixtures import PRODUCT_NAME_2, PRODUCT_PRICE_2, TEST_NUMBER


@pytest.mark.django_db
def test_product_name_filter(client, products):
    filter = f"?name={products[1].name[1:4]}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    # TODO: can't test Unicode case-insensitive comparisons on sqlite DB,
    # TODO: but it works for PostgreSQL
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[1].pk
    assert response.data["results"][0]["name"] == PRODUCT_NAME_2


@pytest.mark.django_db
def test_product_category_filter(client, products, categories):
    filter = f"?category={categories[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert (
        response.data["results"][0]["category"]["category_name"] == categories[1].name
    )


@pytest.mark.django_db
def test_product_category_filter_multiple(client, products, categories):
    filter = f"?category={categories[0].slug}&category={categories[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert (
        response.data["results"][0]["category"]["category_name"] == categories[1].name
    )
    assert response.data["results"][1]["id"] == products[2].pk
    assert response.data["results"][1]["name"] == products[2].name
    assert (
        response.data["results"][1]["category"]["category_name"] == categories[0].name
    )


@pytest.mark.django_db
def test_product_category_filter_fail_invalid_slug(client, categories):
    filter = f"?category={categories[1].slug[:2]}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "category"


@pytest.mark.django_db
def test_product_subcategory_filter(client, products, subcategories):
    filter = f"?subcategory={subcategories[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[2].pk
    assert response.data["results"][0]["name"] == products[2].name
    assert (
        response.data["results"][0]["subcategory"]["subcategory_name"]
        == subcategories[1].name
    )


@pytest.mark.django_db
def test_product_subcategory_filter_multiple(client, products, subcategories):
    filter = f"?subcategory={subcategories[1].slug}&subcategory={subcategories[2].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert (
        response.data["results"][0]["subcategory"]["subcategory_name"]
        == subcategories[2].name
    )
    assert response.data["results"][1]["id"] == products[2].pk
    assert response.data["results"][1]["name"] == products[2].name
    assert (
        response.data["results"][1]["subcategory"]["subcategory_name"]
        == subcategories[1].name
    )


@pytest.mark.django_db
def test_product_subcategory_filter_fail_invalid_slug(client, subcategories):
    filter = f"?subcategory={subcategories[1].slug[:2]}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "subcategory"


@pytest.mark.django_db
def test_product_producer_filter(client, products, producers):
    filter = f"?producer={producers[0].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][0]["producer"]["producer_name"] == producers[0].name


@pytest.mark.django_db
def test_product_producer_filter_multiple(client, products, producers):
    filter = f"?producer={producers[0].slug}&producer={producers[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][0]["producer"]["producer_name"] == producers[0].name
    assert response.data["results"][1]["id"] == products[1].pk
    assert response.data["results"][1]["name"] == products[1].name
    assert response.data["results"][1]["producer"]["producer_name"] == producers[1].name
    assert response.data["results"][2]["id"] == products[2].pk
    assert response.data["results"][2]["name"] == products[2].name
    assert response.data["results"][2]["producer"]["producer_name"] == producers[1].name


@pytest.mark.django_db
def test_product_producer_filter_fail_invalid_slug(client, producers):
    filter = f"?producer={producers[1].slug[:2]}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "producer"


@pytest.mark.django_db
def test_product_components_filter(client, products, components):
    filter = f"?components={components[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[2].pk
    assert response.data["results"][0]["name"] == products[2].name
    assert (
        response.data["results"][0]["components"][0]["component_name"]
        == components[1].name
    )


@pytest.mark.django_db
def test_product_components_filter_multiple(client, products, components):
    filter = f"?components={components[3].slug}&components={components[2].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert (
        response.data["results"][0]["components"][0]["component_name"]
        == components[2].name
    )
    assert (
        response.data["results"][0]["components"][1]["component_name"]
        == components[3].name
    )
    assert response.data["results"][1]["id"] == products[1].pk
    assert response.data["results"][1]["name"] == products[1].name
    assert (
        response.data["results"][1]["components"][0]["component_name"]
        == components[3].name
    )


@pytest.mark.django_db
def test_product_components_filter_fail_invalid_slug(client, components):
    filter = f"?components={components[1].slug[:2]}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "components"


@pytest.mark.django_db
def test_product_tags_filter(client, products, tags):
    products[2].tags.set(tags[0:1])
    filter = f"?tags={tags[0].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[2].pk
    assert response.data["results"][0]["name"] == products[2].name
    assert response.data["results"][0]["tags"][0]["tag_name"] == tags[0].name


@pytest.mark.django_db
def test_product_tags_filter_multiple(client, products, tags):
    products[1].tags.set([tags[1]])
    products[2].tags.set([tags[0]])
    filter = f"?tags={tags[0].slug}&tags={tags[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[1].pk
    assert response.data["results"][0]["name"] == products[1].name
    assert response.data["results"][0]["tags"][0]["tag_name"] == tags[1].name
    assert response.data["results"][1]["id"] == products[2].pk
    assert response.data["results"][1]["name"] == products[2].name
    assert response.data["results"][1]["tags"][0]["tag_name"] == tags[0].name


@pytest.mark.django_db
def test_product_tags_filter_fail_invalid_slug(client, tags):
    filter = f"?tags={tags[1].slug[:2]}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "tags"


@pytest.mark.django_db
def test_product_promotions_filter(client, products, promotions):
    products[1].promotions.set([promotions[0]])
    filter = f"?promotions={promotions[0].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[1].pk
    assert response.data["results"][0]["name"] == products[1].name
    assert (
        response.data["results"][0]["promotions"][0]["promotion_name"]
        == promotions[0].name
    )


@pytest.mark.django_db
def test_product_promotions_filter_multiple(client, products, promotions):
    products[0].promotions.set([promotions[1]])
    products[1].promotions.set([promotions[0]])
    filter = f"?promotions={promotions[0].slug}&promotions={promotions[1].slug}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert (
        response.data["results"][0]["promotions"][0]["promotion_name"]
        == promotions[1].name
    )
    assert response.data["results"][1]["id"] == products[1].pk
    assert response.data["results"][1]["name"] == products[1].name
    assert (
        response.data["results"][1]["promotions"][0]["promotion_name"]
        == promotions[0].name
    )


@pytest.mark.django_db
def test_product_promotions_filter_fail_invalid_slug(client):
    filter = f"?promotions={TEST_NUMBER}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 400
    assert response.data["type"] == "validation_error"
    assert response.data["errors"][0]["code"] == "invalid_choice"
    assert response.data["errors"][0]["attr"] == "promotions"


@pytest.mark.django_db
def test_product_discontinued_filter(client, auth_admin, products):
    payload = {"discontinued": True}
    auth_admin.patch(
        reverse("api:product-detail", kwargs={"pk": products[1].pk}), payload
    )
    filter_true = "?discontinued=1"
    response = client.get(reverse("api:product-list") + filter_true)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[1].pk
    assert response.data["results"][0]["name"] == products[1].name
    assert response.data["results"][0]["discontinued"] is True

    filter_false = "?discontinued=0"
    response = client.get(reverse("api:product-list") + filter_false)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][0]["discontinued"] is False
    assert response.data["results"][1]["id"] == products[2].pk
    assert response.data["results"][1]["name"] == products[2].name
    assert response.data["results"][1]["discontinued"] is False

    filter_invalid = "?discontinued=3"
    response = client.get(reverse("api:product-list") + filter_invalid)

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][0]["discontinued"] is False
    assert response.data["results"][1]["id"] == products[1].pk
    assert response.data["results"][1]["name"] == products[1].name
    assert response.data["results"][1]["discontinued"] is True
    assert response.data["results"][2]["id"] == products[2].pk
    assert response.data["results"][2]["name"] == products[2].name
    assert response.data["results"][2]["discontinued"] is False


@pytest.mark.django_db
def test_product_is_favorited_filter(auth_client, products):
    auth_client.post(reverse("api:product-favorite", kwargs={"pk": products[1].pk}))
    filter_true = "?is_favorited=1"
    response = auth_client.get(reverse("api:product-list") + filter_true)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == products[1].pk
    assert response.data["results"][0]["name"] == products[1].name
    assert response.data["results"][0]["is_favorited"] is True

    filter_false = "?is_favorited=0"
    response = auth_client.get(reverse("api:product-list") + filter_false)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][0]["is_favorited"] is False
    assert response.data["results"][1]["id"] == products[2].pk
    assert response.data["results"][1]["name"] == products[2].name
    assert response.data["results"][1]["is_favorited"] is False

    filter_invalid = "?is_favorited=3"
    response = auth_client.get(reverse("api:product-list") + filter_invalid)

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][0]["is_favorited"] is False
    assert response.data["results"][1]["id"] == products[1].pk
    assert response.data["results"][1]["name"] == products[1].name
    assert response.data["results"][1]["is_favorited"] is True
    assert response.data["results"][2]["id"] == products[2].pk
    assert response.data["results"][2]["name"] == products[2].name
    assert response.data["results"][2]["is_favorited"] is False


@pytest.mark.django_db
def test_product_min_price_filter(client, products):
    filter = f"?min_price={PRODUCT_PRICE_2}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[1].pk
    assert response.data["results"][0]["name"] == products[1].name
    assert response.data["results"][1]["id"] == products[2].pk
    assert response.data["results"][1]["name"] == products[2].name


@pytest.mark.django_db
def test_product_min_price_filter_invalid(client, products):
    filter = f"?min_price={-PRODUCT_PRICE_2}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 3


@pytest.mark.django_db
def test_product_max_price_filter(client, products):
    filter = f"?max_price={PRODUCT_PRICE_2}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == products[0].pk
    assert response.data["results"][0]["name"] == products[0].name
    assert response.data["results"][1]["id"] == products[1].pk
    assert response.data["results"][1]["name"] == products[1].name


@pytest.mark.django_db
def test_product_max_price_filter_invalid(client, products):
    filter = f"?max_price={-PRODUCT_PRICE_2}"
    response = client.get(reverse("api:product-list") + filter)

    assert response.status_code == 200
    assert response.data["count"] == 3
