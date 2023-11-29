import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_product_list(client, products):
    name_filter = "?name=О"
    response = client.get(reverse("api:product-list") + name_filter)

    assert response.status_code == 200
    # TODO: can't test Unicode case-insensitive comparisons on sqlite DB,
    # TODO: but it works for PostgreSQL
    # assert response.data["count"] == 2
