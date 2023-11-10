import pytest
from rest_framework.test import APIClient

from backend.orders.models import ShoppingCart, ShoppingCartProduct
from backend.products.models import Category, Component, Product, Producer, Subcategory, Tag
from backend.users.models import Address, User


# @pytest.fixture
# def user_superuser(django_user_model):
#     return django_user_model.objects.create_superuser(
#         username='TestSuperuser',
#         email='testsuperuser@good_food.fake',
#         password='1234567',
#         role='user',
#         bio='superuser bio'
#     )
#
#
@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin',
        email='testadmin@good_food.fake',
        password='1234567',
        role='admin',
        bio='admin bio'
    )


@pytest.fixture
def moderator(django_user_model):
    return django_user_model.objects.create_user(
        username='TestModerator',
        email='testmoder@good_food.fake',
        password='1234567',
        role='moderator',
        bio='moder bio'
    )


@pytest.fixture
def user():
    address = Address.objects.create(
        address="Saint-Petersburg",
        user=1
    )
    user = User.objects.create(
        username="username",
        email="email@test_mail.ru",
        addrerss=address,
        password="1234"
    )
    return user


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    print(client)
    return client


@pytest.fixture
def anonimus_client(user):
    anonimus_client = APIClient()
    return anonimus_client


@pytest.fixture
def categories():
    Category.objects.create(category_name="Овощи")
    Category.objects.create(category_name="Хлебобулочные изделия")
    Category.objects.create(category_name="Сладости")
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
            carbohydrates=carbohydrates[ind]

        )
        ind += 1

    return Product.objects.all()
