from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
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
        cls.user_2 = User.objects.create(
            username="test_user_2",
            email="test_user@mail_2.ru",
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
        """Сheck access of unauthorized user."""
        response = self.guest_client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.guest_client.get("/api/users/1/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_authorized(self):
        """Сheck access of authorized user."""
        response = self.authorized_client.get("/api/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.authorized_client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.guest_client.get("/api/users/2/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_add_address(self):
        """Check add address for user. Still not work :(."""
        # data = {"first_name": "tessst"}
        # response = self.authorized_client.patch("/api/users/me/", data=data)

    def test_check_user_creation(self):
        """Check user creation."""
        self.created_user = APIClient()
        response = self.created_user.post(
            "/api/users/",
            {
                "username": "creation",
                "email": "creature@mail.ru",
                "password": "admin_12",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(id=response.data["id"])
        self.assertEqual(user.email, "creature@mail.ru")
        self.assertEqual(user.username, "creation")
        self.assertEqual(user.city, "Moscow")

    def test_user_delete(self):
        """Сheck user deletion."""
        response = self.authorized_client.delete("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.authorized_client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
