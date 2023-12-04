import pytest
from rest_framework.test import APIClient

import users
from orders.models import Delivery, ShoppingCart
from products.models import (
    Category,
    Component,
    FavoriteProduct,
    Producer,
    Product,
    Promotion,
    Subcategory,
    Tag,
)
from users.models import Address, User

TEST_NAME = "Test"
TEST_SLUG = "test"
TEST_ADDRESS = "test address"
TEST_TIME = "2023-11-26T10:27:08"
TEST_NUMBER = 275
TEST_TEXT = "Some text"

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
CATEGORY_NAME_3 = "Напитки"
CATEGORY_SLUG_1 = "vegetables"
CATEGORY_SLUG_2 = "bakery"
CATEGORY_SLUG_3 = "beverages"

SUBCATEGORY_NAME_1 = "Помидоры"
SUBCATEGORY_NAME_2 = "Огурцы"
SUBCATEGORY_NAME_3 = "Хлеб дрожжевой"
SUBCATEGORY_NAME_4 = "Вода"
SUBCATEGORY_SLUG_1 = "tomatoes"
SUBCATEGORY_SLUG_2 = "cucumbers"
SUBCATEGORY_SLUG_3 = "yeast-bread"
SUBCATEGORY_SLUG_4 = "water"

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

PRODUCER_NAME_1 = "Выборжец"
PRODUCER_NAME_2 = "Курочкин П.Н."

PRODUCER_SLUG_1 = "vyborgets"
PRODUCER_SLUG_2 = "kurochkin"

PRODUCER_ADDRESS_1 = "Ленинградская область, г. Светогорск, ул. Кирова, д. 8"
PRODUCER_ADDRESS_2 = "г. Москва, Аптекарский огород"

PROMOTION_NAME_1 = "Birthday Discount 15%"
PROMOTION_NAME_2 = "Black Friday"

PROMOTION_DISCOUNT_1 = 15
PROMOTION_DISCOUNT_2 = 20

PRODUCT_NAME_1 = "Батон нарезной"
PRODUCT_NAME_2 = "Вода без газа 0.5 л"
PRODUCT_NAME_3 = "Огурцы короткоплодные 2 шт."

PRODUCT_PRICE_1 = 30
PRODUCT_PRICE_2 = 50
PRODUCT_PRICE_3 = 100

PRODUCT_AMOUNT_1 = 300
PRODUCT_AMOUNT_2 = 500
PRODUCT_AMOUNT_3 = 2


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
def user2(django_user_model):
    return django_user_model.objects.create_user(
        username="Testuser2",
        email="testuser2@good_food.fake",
        password="1234567",
        phone_number="89876543456",
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def auth_client1(client, user2):
    client.force_authenticate(user=user2)
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
        name=SUBCATEGORY_NAME_4, slug=SUBCATEGORY_SLUG_4, parent_category=categories[2]
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
def promotions():
    Promotion.objects.create(
        promotion_type=Promotion.BIRTHDAY,
        name=PROMOTION_NAME_1,
        discount=PROMOTION_DISCOUNT_1,
    )
    Promotion.objects.create(name=PROMOTION_NAME_2, discount=PROMOTION_DISCOUNT_2)
    return Promotion.objects.all()


@pytest.fixture
def producers():
    Producer.objects.create(
        name=PRODUCER_NAME_1,
        slug=PRODUCER_SLUG_1,
        producer_type=Producer.COMPANY,
        address=PRODUCER_ADDRESS_1,
    )
    Producer.objects.create(
        name=PRODUCER_NAME_2,
        slug=PRODUCER_SLUG_2,
        producer_type=Producer.ENTREPRENEUR,
        address=PRODUCER_ADDRESS_2,
    )
    return Producer.objects.all()


@pytest.fixture
def products(subcategories, components, producers):
    bread = Product.objects.create(
        name=PRODUCT_NAME_1,
        category=subcategories[2].parent_category,
        subcategory=subcategories[2],
        producer=producers[0],
        measure_unit=Product.GRAMS,
        amount=PRODUCT_AMOUNT_1,
        price=PRODUCT_PRICE_1,
    )
    bread.components.set(components[2:])
    water = Product.objects.create(
        name=PRODUCT_NAME_2,
        category=subcategories[3].parent_category,
        subcategory=subcategories[3],
        producer=producers[1],
        measure_unit=Product.MILLILITRES,
        amount=PRODUCT_AMOUNT_2,
        price=PRODUCT_PRICE_2,
    )
    water.components.set(components[3:4])
    cucumbers = Product.objects.create(
        name=PRODUCT_NAME_3,
        category=subcategories[1].parent_category,
        subcategory=subcategories[1],
        producer=producers[1],
        measure_unit=Product.ITEMS,
        amount=PRODUCT_AMOUNT_3,
        price=PRODUCT_PRICE_3,
    )
    cucumbers.components.set(components[1:2])
    return Product.objects.all()


@pytest.fixture
def favorites(user, products):
    FavoriteProduct.objects.create(user=user, product=products[0])
    FavoriteProduct.objects.create(user=user, product=products[1])
    return FavoriteProduct.objects.all()


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
    Delivery.objects.create(delivery_point="Test delivery_point")
    Delivery.objects.create(delivery_point="Test delivery_point 1")
    return Delivery.objects.all()
