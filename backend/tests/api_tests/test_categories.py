import pytest
from django.urls import reverse

# from products.models import Category


@pytest.mark.django_db
def test_get_category_list_by_anonymous(client):
    response = client.get(reverse("api:category-list"))

    assert response.status_code == 200
