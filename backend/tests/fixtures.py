import pytest
from rest_framework.test import APIClient

import users
from orders.models import Delivery, ShoppingCart
from products.models import Category, Component, Producer, Product, Subcategory, Tag
from users.models import Address, User

TEST_NAME = "Test"
TEST_SLUG = "test"

INVALID_SLUG = "te st"
INVALID_SLUG_MESSAGE = (
    "Значение должно состоять только из букв, цифр, символов подчёркивания или "
    "дефисов, входящих в стандарт Юникод."
)
INVALID_ID = 1000

USER = "test_user"
USER_EMAIL = "test_user@test.com"
ADMIN = "TestAdmin"
ADMIN_EMAIL = "testadmin@good_food.fake"
PASSWORD = "test_password"
CITY = "Moscow"
FIRST_NAME = "First"
LAST_NAME = "Last"
ADDRESS1 = "Test address 1"
ADDRESS2 = "Test address 2"
BIRTH_DATE = "01.01.2000"
PHONE_NUMBER = "89999999999"

CATEGORY_NAME_1 = "Овощи"
CATEGORY_NAME_2 = "Хлебобулочные изделия"
CATEGORY_NAME_3 = "Сладости"
CATEGORY_SLUG_1 = "vegetables"
CATEGORY_SLUG_2 = "bakery"
CATEGORY_SLUG_3 = "sweets"

SUBCATEGORY_NAME_1 = "Помидоры"
SUBCATEGORY_NAME_2 = "Огурцы"
SUBCATEGORY_NAME_3 = "Хлеб дрожжевой"
SUBCATEGORY_NAME_4 = "Булочки"
SUBCATEGORY_SLUG_1 = "tomatoes"
SUBCATEGORY_SLUG_2 = "cucumbers"
SUBCATEGORY_SLUG_3 = "yeast-bread"
SUBCATEGORY_SLUG_4 = "buns"

COMPONENT_NAME_1 = "помидоры"
COMPONENT_NAME_2 = "огурцы"
COMPONENT_NAME_3 = "мука пшеничная в/с"
COMPONENT_NAME_4 = "вода питьевая"
COMPONENT_NAME_5 = "соль поваренная"
COMPONENT_NAME_6 = "сахар"
COMPONENT_NAME_7 = "дрожжи хлебопекарные"
COMPONENT_NAME_8 = "масло растительное"

COMPONENT_SLUG_1 = "tomato"
COMPONENT_SLUG_2 = "cucumber"
COMPONENT_SLUG_3 = "premium-wheat-flour"
COMPONENT_SLUG_4 = "water"
COMPONENT_SLUG_5 = "table-salt"
COMPONENT_SLUG_6 = "sugar"
COMPONENT_SLUG_7 = "yeast"
COMPONENT_SLUG_8 = "oil"

TAG_NAME_1 = "Для вегетарианцев"
TAG_NAME_2 = "Детское меню"

TAG_SLUG_1 = "vegetarian"
TAG_SLUG_2 = "kids"


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username=ADMIN, email=ADMIN_EMAIL, password=PASSWORD, is_staff=True
    )


@pytest.fixture
def user():
    return User.objects.create_user(username=USER, email=USER_EMAIL, password=PASSWORD)


@pytest.fixture
def user1(django_user_model):
    return django_user_model.objects.create_user(
        username="Testuser1",
        email="testuser1@good_food.fake",
        password="1234567",
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def auth_admin(client, admin):
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def categories():
    Category.objects.create(name=CATEGORY_NAME_1, slug=CATEGORY_SLUG_1)
    Category.objects.create(name=CATEGORY_NAME_2, slug=CATEGORY_SLUG_2)
    Category.objects.create(name=CATEGORY_NAME_3, slug=CATEGORY_SLUG_3)
    return Category.objects.all()


@pytest.fixture
def subcategories(categories):
    Subcategory.objects.create(
        name=SUBCATEGORY_NAME_1, slug=SUBCATEGORY_SLUG_1, parent_category=categories[0]
    )
    Subcategory.objects.create(
        name=SUBCATEGORY_NAME_2, slug=SUBCATEGORY_SLUG_2, parent_category=categories[0]
    )
    Subcategory.objects.create(
        name=SUBCATEGORY_NAME_3, slug=SUBCATEGORY_SLUG_3, parent_category=categories[1]
    )
    Subcategory.objects.create(
        name=SUBCATEGORY_NAME_4, slug=SUBCATEGORY_SLUG_4, parent_category=categories[1]
    )
    return Subcategory.objects.all()


@pytest.fixture
def components():
    Component.objects.create(name=COMPONENT_NAME_1, slug=COMPONENT_SLUG_1)
    Component.objects.create(name=COMPONENT_NAME_2, slug=COMPONENT_SLUG_2)
    Component.objects.create(name=COMPONENT_NAME_3, slug=COMPONENT_SLUG_3)
    Component.objects.create(name=COMPONENT_NAME_4, slug=COMPONENT_SLUG_4)
    Component.objects.create(name=COMPONENT_NAME_5, slug=COMPONENT_SLUG_5)
    Component.objects.create(name=COMPONENT_NAME_6, slug=COMPONENT_SLUG_6)
    Component.objects.create(name=COMPONENT_NAME_7, slug=COMPONENT_SLUG_7)
    Component.objects.create(name=COMPONENT_NAME_8, slug=COMPONENT_SLUG_8)
    return Component.objects.all()


@pytest.fixture
def tags():
    Tag.objects.create(name=TAG_NAME_1, slug=TAG_SLUG_1)
    Tag.objects.create(name=TAG_NAME_2, slug=TAG_SLUG_2)
    return Tag.objects.all()


@pytest.fixture
def producers():
    Producer.objects.create(
        name="Выборжец",
        producer_type="Юридическое лицо",
        address="Ленинградская область",
    )
    Producer.objects.create(
        name="Хлебный дом", producer_type="Юридическое лицо", address="Тверь"
    )
    Producer.objects.create(
        name="Красный Октябрь", producer_type="Юридическое лицо", address="Москва"
    )
    return Producer.objects.all()


@pytest.fixture
def products(user, subcategories, components, tags, producers):
    ind = 0
    price = [100, 140, 120]
    measure_unit = ["гр", "шт", "гр"]
    amount = [1000, 1, 1000]
    carbohydrates = [3.89, 37.7, 43]
    fats = [0.2, 1.4, 37]
    proteins = [0.88, 7.7, 13]
    kcal = [18.0, 201, 560]
    for subcategory in subcategories:
        Product.objects.create(
            user=user,
            subategory=subcategory[ind],
            name=components[ind],
            components=components[ind],
            price=price[ind],
            tags=tags,
            producer=producers[ind],
            measure_unit=measure_unit[ind],
            amount=amount[ind],
            kcal=kcal[ind],
            proteins=proteins[ind],
            fats=fats[ind],
            carbohydrates=carbohydrates[ind],
        )
        ind += 1

    return Product.objects.all()


@pytest.fixture
def shopping_carts(user, admin, products):
    shopping_cart = ShoppingCart.objects.create(user=user)
    shopping_cart.products.set(products)
    shopping_cart = ShoppingCart.objects.create(user=admin)
    shopping_cart.products.set(products)
    return ShoppingCart.objects.all()


@pytest.fixture(scope="session")
def users_db_session(tmpdir_factory):
    """Connect to db before tests, disconnect after."""
    temp_dir = tmpdir_factory.mktemp("temp")
    users.start_tasks_db(str(temp_dir), "tiny")
    yield
    users.stop_tasks_db()


@pytest.fixture()
def tasks_db(tasks_db_session):
    """An empty tasks db."""
    users.delete_all()


@pytest.fixture
def address(user):
    return Address.objects.create(address="Saint-Petersburg", user=user)


@pytest.fixture
def delivery_points(user):
    return Delivery.objects.create(delivery_point="Test delivery_point")
