from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import Address

User = get_user_model()


class UsersTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username="test_user",
            email="test_user@mail.ru",
            password="admin_12",
        )

        cls.address = Address.objects.create(
            address="test_address",
            user=cls.user,
        )

    def setUp(self):
        self.guest_client = APIClient()

        self.authorized_client = APIClient()
        self.authorized_client.post(
            "/api/users/",
            {
                "username": "test",
                "email": "test_user_1@mail.ru",
                "password": "admin_12",
            },
        )
        response = self.authorized_client.post(
            "/api/token/login/",
            {"email": "test_user_1@mail.ru", "password": "admin_12"},
        )
        token = response.data["auth_token"]
        self.user = self.authorized_client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

    def test_users_not_authorized(self):
        response = self.guest_client.get("/api/users/")
        self.assertEqual(response.status_code, 401)

        response = self.guest_client.get("/api/users/1/")
        self.assertEqual(response.status_code, 401)

    def test_users_authorized(self):
        response = self.authorized_client.get("/api/users/")

        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get("/api/users/me/")
        self.assertEqual(response.status_code, 200)
        print(response.data)

    def test_user_add_address(self):
        data = {"first_name": "tessst"}
        response = self.authorized_client.patch("/api/users/me/", data=data)
        print(response.data)
