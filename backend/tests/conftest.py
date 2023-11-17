import pytest
from rest_framework.test import APIClient

from users.models import User

USERNAME = "test_user"
EMAIL = "test_user@test.com"
PASSWORD = "test_password"


@pytest.fixture
def user():
    return User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)


@pytest.fixture
def client():
    return APIClient()
