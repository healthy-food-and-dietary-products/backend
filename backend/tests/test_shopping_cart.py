import pytest
from rest_framework import status


@pytest.mark.django_db
class TestShoppingCart:

    def test_create_shopping_cart_auth_client(self, auth_client, products, user):
        data = {
                "products": [{"id": products[0].id, "quantity": 2},
                             {"id": products[1].id, "quantity": 4}]}
        response = auth_client.post(
            f"/users/{user.id}/shopping_cart/", data,
            format="json")

        data = response.json()
        assert len(data["products"]) == 2
        # assert products.values("id") in data
        # assert "user" in data
        assert response.status_code == status.HTTP_201_CREATED

        #

        # assert ShoppingCart.user == auth_client
        # assert "products" in data


    def test_create_shopping_cart_admin(self, admin, user, products):

        shopping_cart_data = {
                "products": [{"id": products[0].id, "quantity": 2},
                             {"id": products[1].id, "quantity": 4}]}
        response = admin.post(
            f"/users/{user.id}/shopping_cart/", shopping_cart_data,
            format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert "user" in data
        assert data["user"] == user.id
        assert "products" in data
        assert len(data["products"]) == 2

    def test_create_shopping_cart_anonimus(
            self, anonimus_client, user, products):
        shopping_cart_data = {
                "products": [{"id": products[0].id, "quantity": 2},
                             {"id": products[1].id, "quantity": 4}]}
        response = anonimus_client.post(
            f"/users/{user.id}/shopping_cart/", shopping_cart_data,
            format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_shopping_cart(self, auth_client, shopping_cart, products, user):
        updated_quantity = 10
        data = {"products": [
                {"id": products[0].id, "quantity": updated_quantity}]}
        endpoint = f"/users/{user.id}/shopping_cart/{shopping_cart.id}"
        response = auth_client.patch(endpoint, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        response = auth_client.get(f"/users/{user.id}/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        updated_product = data["products"][0]
        assert updated_product["quantity"] == updated_quantity

    def test_get_shopping_cart(self, auth_client, user):

        response = auth_client.get(f"/users/{user.id}/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.user == auth_client

    def test_delete_shopping_cart(self, auth_client, shopping_cart, user):
        endpoint = f"/users/{user.id}/shopping_cart/{shopping_cart.id}"
        response = auth_client.delete(endpoint)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = auth_client.get(endpoint)
        assert response.status_code == status.HTTP_404_NOT_FOUND
