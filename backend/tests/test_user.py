import pytest
from rest_framework.test import APIClient
from rest_framework import status

client = APIClient()

@pytest.mark.django_db(transaction=True)
class TestUser:
    def test_create_user():
        payload = {
                "username": "creation",
                "email": "creature@mail.ru",
                "password": "admin_12",
        } 
        url = "/api/users/"
        response = client.post(url, payload)
        data = response.data
        assert response.status_code != status.HTTP_201_CREATED
        # user = User.objects.get(id=response.data["id"])
        # self.assertEqual(user.email, "creature@mail.ru")
        # self.assertEqual(user.username, "creation")
        # self.assertEqual(user.city, "Moscow")
