import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_product_list(client, products):
    response = client.get(reverse("api:product-list"))

    assert response.status_code == 200
