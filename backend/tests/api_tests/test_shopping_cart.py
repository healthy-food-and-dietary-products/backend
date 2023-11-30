import pytest
from rest_framework import status


@pytest.mark.django_db(transaction=True)
class TestShoppingCart:
    def test_create_shopping_cart_auth_client(self, auth_client, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 2},
                {"id": products[1].id, "quantity": 4},
            ]
        }
        response = auth_client.post(
            "/api/shopping_cart/", shopping_cart_data, format="json"
        )
        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 2
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_shopping_cart_anonimous_user(self, client, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 1},
                {"id": products[1].id, "quantity": 3},
            ]
        }
        response = client.post("/api/shopping_cart/", shopping_cart_data, format="json")
        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 2
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_shopping_cart_by_authirized_user(self, auth_client, products):
        updated_quantity = 10
        updated_shopping_cart_data = {
            "products": [{"id": products[0].id, "quantity": updated_quantity}]
        }
        endpoint = "/api/shopping_cart/"
        response = auth_client.post(endpoint, updated_shopping_cart_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        response = auth_client.get("/api/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        updated_product = data["products"][0]
        assert updated_product["quantity"] == updated_quantity

    def test_update_shopping_cart_by_anonimous_user(self, client, products):
        updated_quantity = 10
        updated_shopping_cart_data = {
            "products": [{"id": products[0].id, "quantity": updated_quantity}]
        }
        endpoint = "/api/shopping_cart/"
        response = client.post(endpoint, updated_shopping_cart_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        response = client.get("/api/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        updated_product = data["products"][0]
        assert updated_product["quantity"] == updated_quantity

    def test_get_shopping_cart_by_authorized_user(self, auth_client):
        response = auth_client.get("/api/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK

    def test_get_shopping_cart_by_anonimous_user(self, client):
        response = client.get("/api/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_shopping_cart_by_anonimous_user(self, client, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 1},
                {"id": products[1].id, "quantity": 3},
            ]
        }
        response = client.post("/api/shopping_cart/", shopping_cart_data, format="json")
        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 2
        assert response.status_code == status.HTTP_201_CREATED
        product_remove = products[0].id
        endpoint = f"/api/shopping_cart/{product_remove}"
        response = client.delete(endpoint, product_remove, format="json")
        response = client.get("/api/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert product_remove not in data

    def test_delete_shopping_cart_by_authorized_user(self, auth_client, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 1},
                {"id": products[1].id, "quantity": 3},
            ]
        }
        response = auth_client.post(
            "/api/shopping_cart/", shopping_cart_data, format="json"
        )
        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 2
        assert response.status_code == status.HTTP_201_CREATED
        product_remove = products[0].id
        endpoint = f"/api/shopping_cart/{product_remove}"
        response = auth_client.delete(endpoint, product_remove, format="json")
        response = auth_client.get("/api/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert product_remove not in data
