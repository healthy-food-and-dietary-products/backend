import pytest
from rest_framework import status
from rest_framework.test import APIClient
from orders.models import ShoppingCart, ShoppingCartProduct, Order


@pytest.mark.django_db(transaction=True)
class TestOrder:

    def test_create_order_auth_client(self, auth_client, user,
                                      shopping_carts, delivery_points):
        order_data = {"payment_method": "Payment at the point of delivery",
                      "delivery_method": "Point of delivery",
                      "package": 0,
                      "comment": "",
                      "delivery_point": delivery_points.id}
        response = auth_client.post(
            f"/api/users/{user.id}/order/", order_data,
            format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        order = Order.objects.get()
        assert user.id == order.user.id
        assert order.status == "Ordered"
        assert data["shopping_cart"]["id"] == order.shopping_cart.id

    def test_create_order_another_auth_client(self, auth_client, user1,
                                              shopping_carts, delivery_points):
        order_data = {"payment_method": "Payment at the point of delivery",
                      "delivery_method": "Point of delivery",
                      "package": 0,
                      "comment": "",
                      "delivery_point": delivery_points.id}
        response = auth_client.post(
            f"/api/users/{user1.id}/order/", order_data,
            format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_order_moderator(self, admin, user,
                                    shopping_carts, delivery_points):
        order_data = {"payment_method": "Payment at the point of delivery",
                      "delivery_method": "Point of delivery",
                      "package": 0,
                      "comment": "",
                      "delivery_point": delivery_points.id}
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post(
            f"/api/users/{admin.id}/order/", order_data,
            format="json")
        data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get()
        assert admin.id == order.user.id
        assert order.status == "Ordered"
        assert data["shopping_cart"]["id"] == order.shopping_cart.id

    def test_create_order_anonimus_client(self, anonimus_client, user,
                                          shopping_carts, delivery_points):
        order_data = {"payment_method": "Payment at the point of delivery",
                      "delivery_method": "Point of delivery",
                      "package": 0,
                      "comment": "",
                      "delivery_point": delivery_points.id}
        response = anonimus_client.post(
            f"/api/users/{user.id}/order/", order_data,
            format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_order_auth_client(self, auth_client, user,
                                      shopping_carts, delivery_points):
        order_data = {"payment_method": "Payment at the point of delivery",
                      "delivery_method": "Point of delivery",
                      "package": 0,
                      "comment": "",
                      "delivery_point": delivery_points.id}
        auth_client.post(
            f"/api/users/{user.id}/order/", order_data,
            format="json")
        order = Order.objects.get()
        response = auth_client.delete(
            f"/api/users/{user.id}/order/{order.id}/",
            format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_order_another_auth_client(self, auth_client, user1, user,
                                              shopping_carts, delivery_points):
        order_data = {"payment_method": "Payment at the point of delivery",
                      "delivery_method": "Point of delivery",
                      "package": 0,
                      "comment": "",
                      "delivery_point": delivery_points.id}
        auth_client.post(
            f"/api/users/{user.id}/order/", order_data,
            format="json")
        order = Order.objects.get()
        client = APIClient()
        client.force_authenticate(user=user1)
        response = client.delete(
            f"/api/users/{user.id}/order/{order.id}/",
            format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
