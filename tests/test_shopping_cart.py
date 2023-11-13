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
            f"/users/{auth_client.id}/shopping_cart/", shopping_cart_data, format="json"
        )
        data = response.json()
        assert "id" in data
        assert "user" in data
        assert data["user"] == auth_client.id
        assert "products" in data
        assert len(data["products"]) == 2
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_shopping_cart_admin(self, admin, user, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 2},
                {"id": products[1].id, "quantity": 4},
            ]
        }
        response = admin.post(
            f"/users/{user.id}/shopping_cart/", shopping_cart_data, format="json"
        )
        data = response.json()
        assert "id" in data
        assert "user" in data
        assert data["user"] == user.id
        assert "products" in data
        assert len(data["products"]) == 2
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_shopping_cart_anonimus(self, anonimus_client, user, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 2},
                {"id": products[1].id, "quantity": 4},
            ]
        }
        response = anonimus_client.post(
            f"/users/{anonimus_client.id}/shopping_cart/",
            shopping_cart_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_shopping_cart(self, auth_client, shopping_cart, products, user):
        updated_quantity = 10
        updated_shopping_cart_data = {
            "products": [{"id": products[0].id, "quantity": updated_quantity}]
        }
        endpoint = f"/users/{auth_client.id}/shopping_cart/{shopping_cart.id}"
        response = auth_client.patch(
            endpoint, updated_shopping_cart_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK

        response = auth_client.get(f"/users/{auth_client.id}/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        updated_product = data["products"][0]
        assert updated_product["quantity"] == updated_quantity

    def test_get_shopping_cart(self, auth_client):
        response = auth_client.get(f"/users/{auth_client.id}/shopping_cart/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.user.id == auth_client.id


#
# @pytest.mark.parametrize('http_method', ('post', 'patch'))
# def test_delete_mine_basket(auth_client, shopping_cart, user):
#     endpoint = f"{SHOPPING_CART_ENDPOINT}mine/"
#     response = auth_client.delete(endpoint)
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#
#     response = auth_client.get(endpoint)
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#
#
#
#
#
# def test_delete_product_in_mine_basket(auth_client, basket, product, user):
#     updated_basket_data = {"basket_products": []}
#     endpoint = f"{SHOPPING_CART_ENDPOINT}mine/"
#     response = auth_client.put(endpoint, updated_basket_data, format="json")
#     assert response.status_code == status.HTTP_200_OK
#
#     response = auth_client.get(endpoint)
#     assert response.status_code == status.HTTP_200_OK
#
#     data = response.json()
#     assert "basket_products" in data
#     assert len(data["basket_products"]) == 0
#
#
# def test_get_shopping_cart(auth_client, shopping_cart, user):
#     endpoint = f"{SHOPPING_CART_ENDPOINT}mine/"
#     response = auth_client.get(endpoint)
#     assert response.status_code == status.HTTP_200_OK
