import pytest
import users
from rest_framework.test import APIClient
from orders.models import ShoppingCart, ShoppingCartProduct, Delivery, Order
from products.models import Category, Component, Product, Producer, Subcategory, Tag
from users.models import Address, User


@pytest.fixture(scope='session')
def users_db_session(tmpdir_factory):
    """Connect to db before tests, disconnect after."""
    temp_dir = tmpdir_factory.mktemp('temp')
    users.start_tasks_db(str(temp_dir), 'tiny')
    yield
    users.stop_tasks_db()

@pytest.fixture()
def tasks_db(tasks_db_session):
    """An empty tasks db."""
    users.delete_all()


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='Testuser',
        email='testuser@good_food.fake',
        password='1234567',
        role='user'
    )


@pytest.fixture
def user1(django_user_model):
    return django_user_model.objects.create_user(
        username='Testuser1',
        email='testuser1@good_food.fake',
        password='1234567',
        role='user'
    )


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestAdmin',
        email='testadmin@good_food.fake',
        password='1234567',
        role='admin'
    )


@pytest.fixture
def moderator(django_user_model):
    return django_user_model.objects.create_user(
        username='TestModerator',
        email='testmoder@good_food.fake',
        password='1234567',
        role='moderator'
    )


@pytest.fixture
def address(user):
    address = Address.objects.create(
        address="Saint-Petersburg",
        user=user
    )
    return address


@pytest.fixture
def delivery_points(user):
    delivery_point = Delivery.objects.create(
        delivery_point="Test delivery_point"
    )
    return delivery_point


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def anonimus_client(user):
    anonimus_client = APIClient()
    return anonimus_client


@pytest.fixture
def categories():
    Category.objects.create(name="Овощи")
    Category.objects.create(name="Хлебобулочные изделия")
    Category.objects.create(name="Сладости")
    return Category.objects.all()


@pytest.fixture
def subcategories(categories):
    Subcategory.objects.create(
        name="Помидоры",
        parent_category=categories[0]
    )
    Subcategory.objects.create(
        name="Хлеб",
        parent_category=categories[1]
    )
    Subcategory.objects.create(
        name="Халва",
        parent_category=categories[2]
    )
    return Subcategory.objects.all()


@pytest.fixture
def components():
    Component.objects.create(name="Помидоры")
    Component.objects.create(name="Хлеб")
    Component.objects.create(name="Халва")
    return Component.objects.all()


@pytest.fixture
def tags():
    Tag.objects.create(name="Витамины")
    Tag.objects.create(name="Полезно")
    return Tag.objects.all()


@pytest.fixture
def producers():
    Producer.objects.create(
        name="Выборжец",
        producer_type="Юридическое лицо",
        address="Ленинградская область"
    )
    Producer.objects.create(
        name="Хлебный дом",
        producer_type="Юридическое лицо",
        address="Тверь"
    )
    Producer.objects.create(
        name="Красный Октябрь",
        producer_type="Юридическое лицо",
        address="Москва"
    )
    return Producer.objects.all()


@pytest.fixture
def products(user, categories, subcategories, components, tags, producers):
    ind = 0
    price = [100, 140, 120]
    measure_unit = ["гр", "шт", "гр"]
    amount = [1000, 1, 1000]
    carbohydrates = [3.89, 37.7, 43]
    fats = [0.2, 1.4, 37]
    proteins = [0.88, 7.7, 13]
    kcal = [18.0, 201, 560]
    for subcategorie in subcategories:
        product = Product.objects.create(
            category=categories[ind],
            subcategory=subcategorie,
            name=components[ind],
            price=price[ind],
            producer=producers[ind],
            measure_unit=measure_unit[ind],
            amount=amount[ind],
            kcal=kcal[ind],
            proteins=proteins[ind],
            fats=fats[ind],
            carbohydrates=carbohydrates[ind]
        )
        for tag in tags:
            product.tags.add(tag)
        product.components.set(components)
        ind += 1
    return Product.objects.all()

@pytest.fixture
def shopping_carts(user, admin, products):
    shopping_cart = ShoppingCart.objects.create(user=user)
    shopping_cart.products.set(products)
    shopping_cart = ShoppingCart.objects.create(user=admin)
    shopping_cart.products.set(products)
    return ShoppingCart.objects.all()
