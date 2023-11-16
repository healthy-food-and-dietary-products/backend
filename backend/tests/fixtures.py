import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from products.models import Category, Component, Product, Producer, Subcategory, Tag
from users.models import Address, User


@pytest.fixture
def admin(django_user_model):
    admin = django_user_model.objects.create_superuser(
        username='TestAdmin',
        email='testadmin@good_food.fake',
        password='1234567',
        role='admin',
    )
    admin = APIClient(admin)
    admin.force_authenticate(user=admin)
    return admin


@pytest.fixture
def moderator(django_user_model):
    return django_user_model.objects.create_user(
        username='TestModerator',
        email='testmoder@good_food.fake',
        password='1234567',
        role='moderator',
    )


@pytest.fixture
def get_or_create_token(db, create_user):
    user = create_user()
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def user():
    return User.objects.create(
        username="username",
        email="email@test_mail.ru",
        password="1234"
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def anonimus_client(user):
    return APIClient()



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
def products(categories, subcategories, components, tags, producers):
    price = [100, 140, 120]
    measure_unit = ["гр", "шт", "гр"]
    amount = [1000, 1, 1000]
    carbohydrates = [3.89, 37.7, 43]
    fats = [0.2, 1.4, 37]
    proteins = [0.88, 7.7, 13]
    kcal = [18.0, 201, 560]
    for id in range(len(price)):
        Product.objects.create(
            category=categories[id],
            subcategory=subcategories[id],
            name=components[id],
            price=price[id],
            producer=producers[id],
            measure_unit=measure_unit[id],
            amount=amount[id],
            kcal=kcal[id],
            proteins=proteins[id],
            fats=fats[id],
            carbohydrates=carbohydrates[id]
        )

    return Product.objects.all()
