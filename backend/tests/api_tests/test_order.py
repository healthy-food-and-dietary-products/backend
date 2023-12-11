import pytest
from rest_framework import status
from rest_framework.test import APIClient

from orders.models import Order
from tests.fixtures import ADDRESS1, FIRST_NAME, LAST_NAME, PHONE_NUMBER, USER_EMAIL


@pytest.mark.django_db(transaction=True)
class TestOrder:
    def create_shopping_cart_authorized(self, auth_client_first, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 2},
                {"id": products[1].id, "quantity": 4},
            ]
        }
        response = auth_client_first.post(
            "/api/shopping_cart/", shopping_cart_data, format="json"
        )
        return response.json()

    def create_shopping_cart_anonimous(self, client, products):
        shopping_cart_data = {
            "products": [
                {"id": products[0].id, "quantity": 2},
                {"id": products[1].id, "quantity": 4},
            ]
        }
        response = client.post("/api/shopping_cart/", shopping_cart_data, format="json")
        return response.json()

    def test_create_order_auth_client(self, auth_client_first, products):
        order_data = {
            "payment_method": "In getting by cash",
            "delivery_method": "By courier",
            "package": 200,
            "comment": "After 14:00",
            "add_address": "Saint-Peterburg",
        }
        self.create_shopping_cart_authorized(auth_client_first, products)
        response = auth_client_first.post("/api/order/", order_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get()
        assert order.status == "Ordered"
        assert order.delivery_method == "By courier"
        assert order.payment_method == "In getting by cash"
        assert order.package == 200
        assert order.comment == "After 14:00"
        assert order.add_address == "Saint-Peterburg"

    def test_create_order_anonimus_client(self, client, products, delivery_points):
        user_data = {
            "first_name": FIRST_NAME,
            "last_name": LAST_NAME,
            "phone_number": PHONE_NUMBER,
            "email": USER_EMAIL,
        }
        order_data = {
            "user_data": user_data,
            "payment_method": "In getting by cash",
            "delivery_method": "By courier",
            "package": 0,
            "comment": "",
            "add_address": ADDRESS1,
        }
        self.create_shopping_cart_anonimous(client, products)
        response = client.post("/api/order/", order_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get()
        assert order.status == "Ordered"
        assert order.delivery_method == "By courier"
        assert order.payment_method == "In getting by cash"

    def test_create_order_another_anonimus_client(
        self, client, products, delivery_points
    ):
        user_data = {
            "first_name": FIRST_NAME,
            "last_name": LAST_NAME,
            "phone_number": PHONE_NUMBER,
            "email": USER_EMAIL,
        }
        order_data = {
            "user_data": user_data,
            "payment_method": "Payment at the point of delivery",
            "delivery_method": "Point of delivery",
            "package": 200,
            "delivery_point": delivery_points[0].id,
        }
        self.create_shopping_cart_anonimous(client, products)
        response = client.post("/api/order/", order_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get()
        assert order.status == "Ordered"
        assert order.delivery_method == "Point of delivery"
        assert order.payment_method == "Payment at the point of delivery"

    def test_delete_order_auth_client(
            self, auth_client_first, products, delivery_points):
        order_data = {
            "payment_method": "In getting by cash",
            "delivery_method": "By courier",
            "package": 200,
            "comment": "After 14:00",
            "add_address": "Saint-Peterburg",
        }
        self.create_shopping_cart_authorized(auth_client_first, products)
        auth_client_first.post("/api/order/", order_data, format="json")
        order = Order.objects.get()
        response = auth_client_first.delete(f"/api/order/{order.id}/", format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_order_another_auth_client(
        self, auth_client_first, user1, user, delivery_points, products
    ):
        order_data = {
            "payment_method": "In getting by cash",
            "delivery_method": "By courier",
            "package": 200,
            "comment": "After 14:00",
            "add_address": "Saint-Peterburg",
        }
        self.create_shopping_cart_authorized(auth_client_first, products)
        auth_client_first.post("/api/order/", order_data, format="json")
        order = Order.objects.get()
        client = APIClient()
        client.force_authenticate(user=user1)
        response = client.delete(f"/api/order/{order.id}/", format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_order_anonimus_client(self, client, products, delivery_points):
        user_data = {
            "first_name": FIRST_NAME,
            "last_name": LAST_NAME,
            "phone_number": PHONE_NUMBER,
            "email": USER_EMAIL,
        }
        order_data = {
            "user_data": user_data,
            "payment_method": "In getting by cash",
            "delivery_method": "By courier",
            "package": 0,
            "comment": "",
            "add_address": ADDRESS1,
        }
        self.create_shopping_cart_anonimous(client, products)
        response = client.post("/api/order/", order_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get()
        response = client.delete(f"/api/order/{order.id}/", format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
