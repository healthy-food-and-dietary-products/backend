# good-food

![good_food workflow](https://github.com/healthy-food-and-dietary-products/backend/actions/workflows/good_food_workflow.yaml/badge.svg)


## Локальный запуск приложения в контейнерах

### Клонирование репозитория backend на локальный компьютер

_Важно: при работе в Linux или через терминал WSL2 все команды docker и docker compose нужно выполнять от имени суперпользователя — начинайте их с sudo._

Склонировать репозиторий на свой компьютер и перейти в него:
```
git clone git@github.com:healthy-food-and-dietary-products/backend.git
cd backend
```

### Создание файла с переменными окружения

Перейти в папку infra командой cd infra и создать в ней файл .env с переменными 
окружения, необходимыми для работы приложения в docke-контейнерах.

В переменную EMAIL_HOST_USER нужно вписать адрес электронной почты на yandex,
это нужно для рассылки приложением писем пользователям об активации аккаунта,
о смене пароля или адреса электронной почты, о восстановлении пароля, об оформленных заказах.
На данный момент рассылка писем не подключена, но она планируется в ближайшем будущем.

В переменную EMAIL_HOST_PASSWORD нужно вписать пароль приложения для рассылки писем 
с почтового ящика на yandex. Это не пароль от почтового ящика, его нужно специально 
создать в вашем [Яндекс ID](https://id.yandex.ru/), где нужно найти заголовок 
Безопасность -> Доступ к вашим данным -> 
[Пароли приложений](https://id.yandex.kz/security/app-passwords)
-> Создать пароль приложения -> Почта. Нужно будет придумать имя пароля приложения,
например, test, а затем скопировать полученный пароль.

Переменные STRIPE_PUBLISHABLE_KEY и STRIPE_WEBHOOK_SECRET используются для онлайн-оплаты 
заказов через [Stripe](https://stripe.com/).
Переменная STRIPE_PUBLISHABLE_KEY требуется для создания сессии с оплатой.
Для ее получения нужно [зарегистрироваться на Stripe](https://dashboard.stripe.com/register),
перейти на страницу для разработчиков с 
[ключами от апи](https://dashboard.stripe.com/test/apikeys) и скопировать 
значение Publishable key.
Переменная STRIPE_WEBHOOK_SECRET используется для проверки успешности оплаты 
с помощью вебхука Stripe.
При локальном запуске приложения в docker-контейнерах проверка вебхуком осуществляется 
с помощью Stripe CLI. Нужно [установить Stripe CLI на свой компьютер](https://stripe.com/docs/stripe-cli),
затем открыть терминал и выполнить команду stripe login, в ответ вам будет предложено 
нажать на Enter, после чего в браузере откроется страница для подтвержения вашего 
согласия/несогласия на предоставление Stripe CLI информации о вашем аккаунте Stripe. 
Нужно нажать на кнопку Allow access, и в следующем окне появится сообщение Access granted.
Затем в том же терминале нужно выполнить следующую команду, чтобы процесс 
проверки вебхуком запустился: stripe listen --forward-to localhost:80/webhooks/stripe/
В ответе терминала на данную команду будет нужный ключ:
"Your webhook signing secret is whsec_<...>". 
Вам нужно будет вставить его в переменную STRIPE_WEBHOOK_SECRET.

Переменные VITE_API_URL и VITE_BASE_URL нужны для создания docker-образа с фронтендом 
сайта. Их значения нужно оставить такими, как в примере ниже.
Также нужно склонировать себе на компьютер 
[репозиторий frontend](https://github.com/healthy-food-and-dietary-products/frontend)
командой git clone git@github.com:healthy-food-and-dietary-products/frontend.git
На вашем компьютере репозитории backend и frontend должны находиться в одной и той же 
папке, например, так:
```
Dev              (какая-то общая папка)
 |--backend/     (репозиторий с бэкендом)
 |--frontend/    (репозиторий с фронтендом)
```

Пример содержимого .env файла:
```
SECRET_KEY=key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EMAIL_HOST_USER=<ваш емейл>
EMAIL_HOST_PASSWORD=<ваш пароль>
MODE=prod
DOCKER=yes
ALLOWED_HOSTS=localhost web
CSRF_TRUSTED_ORIGINS=http://localhost/*
STRIPE_PUBLISHABLE_KEY=pk_test_<набор цифр и букв>
STRIPE_WEBHOOK_SECRET=whsec_<набор цифр и букв>
VITE_API_URL=http://localhost:80/api
VITE_BASE_URL=http://localhost:80
```

### Создание и запуск docker-контейнеров

Перейти в папку /infra/ и запустить локальную сборку контейнеров с помощью 
docker compose: 
```
cd infra
docker compose -f docker-compose.local.yml up -d --build
```
После этого будут созданы и запущены в фоновом режиме контейнеры 
(good_food_db, good_food_api, good_food_frontend и good_food_nginx). 
Контейнер good_food_frontend выполнит сборку файлов для фронтенда и остановится.
Остальные контейнеры продолжат работать.

Внутри контейнера web выполнить миграции и создать админа-суперпользователя для входа 
в Админку:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Также требуется [скачать](https://disk.yandex.kz/d/3pMfTcldvUNuJw) папку со статикой бэкенда,
разорхивировать её и из директории, в которой лежит разорхивированная папка static,
скопировать её внутрь контейнера good_food_api следующей командой:
```
docker cp static/ good_food_api:/app
```

После этого Админка должна быть доступна по адресу: http://localhost/admin/
API Root будет доступен по адресу: http://localhost/api/

### Остановка контейнеров

Для остановки работы приложения можно набрать в терминале команду Ctrl+C 
либо открыть второй терминал и воспользоваться командой
```
docker compose stop 
```
Снова запустить контейнеры без их пересборки можно командой
```
docker compose start 
```

### Динамическая документация api 

- Swagger - http://localhost/api/swagger/
- Redoc - http://localhost/api/redoc/


## Пользователи

### Создание пользователей

Создание пользователя доступно по эндоинту /api/users/
Для создания пользователя необходимо POST-запросом отправить следующие обязательные поля:
- email
- username
- password

Помимо этих полей обязательным при регистрации пользователя является поле "city",
в котором в настоящий момент автоматически указывается "Moscow". 

Пример POST-запроса:
```
{
  "email": "testuser@example.com",
  "username": "testuser",
  "password": "string_123"
}
```

Пример ответа:
```
{
  "email": "testuser@example.com",
  "id": 7,
  "username": "testuser",
  "city": "Moscow"
}
```

### Аутентификация пользователей

Аутентификация пользователя доступна по эндпойнту /api/token/login/
Для аутентификации необходимо POST-запросом отправить следующие обязательные поля:
- email
- password

Пример POST-запроса:
```
{
  "password": "string_123",
  "email": "testuser@example.com"
}
```

Пример ответа:
```
{
  "auth_token": "<набор букв и цифр>"
}
```

Чтобы авторизоваться по полученному токену в Swagger или в Postman, нужно передать в заголовок
Authorization значение "Token <токен>", например, "Token 45645hylijglu54545" (без кавычек).

Для отзыва токена авторизации авторизованный пользователь должен выполнить 
POST-запрос без передачи каких-либо полей на эндпойнт /api/token/logout/

### Личный кабинет пользователя

Личный кабинет авторизованного пользователя доступен по эндпойнту /api/users/me/
Там можно посмотреть информацию о себе (GET-запрос), отредактировать её
(PUT- и PATCH-запросы), в том числе путем добавления новых адресов для доставки,
а также удалить пользователя (DELETE-запрос).

Поля, доступные для редактирования:
- username;
- email;
- first_name;
- last_name;
- city;  (в настоящее время единственный допустимый вариант - "Moscow")
- birth_date;
- addresses;
- phone_number; 
- photo.

#### Просмотр личных данных

Просмотр личных данных доступен авторизованному пользователю в отношении себя.
Для этого требуется отправить GET-запрос без передачи каких-либо полей на эндпойнт /api/users/me/

Пример ответа на GET-запрос на просмотр личных данных:
```
{
  "id": 7,
  "username": "testuser",
  "email": "testuser@example.com",
  "first_name": "",
  "last_name": "",
  "city": "Moscow",
  "birth_date": null,
  "addresses": [],
  "address_quantity": 0,
  "phone_number": "",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

Если пользователь является админом, он может получить информацию обо всех зарегистрированных 
пользователях сайта, направив GET-запрос без передачи каких-либо полей на эндпойнт /api/users/
Также админ может просматривать данные конкретного зарегистрированного пользователя,
направив GET-запрос на эндпойнт /api/users/{id}/, например, /api/users/7/.

#### Редактирование своих личных данных

Авторизованный пользователь может менять значение отдельных полей своих личных данных 
с помощью PATCH-запроса на эндпойнт /api/users/me/

Пример PATCH-запроса на изменение username:
```
{
  "username": "testuseruser"
}
```

Пример ответа:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "testuser@example.com",
  "first_name": "string555",
  "last_name": "",
  "city": "Moscow",
  "birth_date": null,
  "addresses": [],
  "address_quantity": 0,
  "phone_number": "",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

Пример PATCH-запроса на изменение birth_date (нужно использовать формат даты DD.MM.YYYY):
```
{
  "birth_date": "01.05.1990"
}
```

Пример ответа:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "testuser@example.com",
  "first_name": "string555",
  "last_name": "",
  "city": "Moscow",
  "birth_date": "01.05.1990",
  "addresses": [],
  "address_quantity": 0,
  "phone_number": "",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

Пример PATCH-запроса на добавление/изменение адресов доставки:
```
{
  "addresses": [
    {
      "address": "Адрес 1",
      "priority_address": true
    },
    {
      "address": "Адрес 2",
      "priority_address": false
    }
  ]
}
```

Пример ответа:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "testuser@example.com",
  "first_name": "string555",
  "last_name": "",
  "city": "Moscow",
  "birth_date": "01.05.1990",
  "addresses": [
    {
      "id": 5,
      "address": "Адрес 1",
      "priority_address": true
    },
    {
      "id": 6,
      "address": "Адрес 2",
      "priority_address": false
    }
  ],
  "address_quantity": 2,
  "phone_number": "",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

Пример PATCH-запроса на удаление адресов доставки:
```
{
  "addresses": []
}
```

Пример ответа:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "testuser@example.com",
  "first_name": "string555",
  "last_name": "",
  "city": "Moscow",
  "birth_date": "01.05.1990",
  "addresses": [],
  "address_quantity": 0,
  "phone_number": "",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

Пример PATCH-запроса на изменение номера телефона 
(допустимые форматы: +7XXXXXXXXXX, 7XXXXXXXXXX, 8XXXXXXXXXX):
```
{
  "phone_number": "88008888888"
}
```

Пример ответа:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "testuser@example.com",
  "first_name": "string555",
  "last_name": "",
  "city": "Moscow",
  "birth_date": "01.05.1990",
  "addresses": [],
  "address_quantity": 0,
  "phone_number": "88008888888",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

PUT-запросом можно редактировать те же самые поля личных данных, но потребуется заполнить 
**все** изменяемые поля.

Пример PUT-запроса на изменение личных данных:
```
{
  "username": "testuseruser",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "city": "Moscow",
  "birth_date": "11.11.2011",
  "addresses": [
    {
      "address": "string",
      "priority_address": true
    }
  ],
  "phone_number": "71177748879"
}
```

Пример ответа:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "city": "Moscow",
  "birth_date": "11.11.2011",
  "addresses": [
    {
      "id": 7,
      "address": "string",
      "priority_address": true
    }
  ],
  "address_quantity": 1,
  "phone_number": "71177748879",
  "photo": "http://127.0.0.1:8000/media/default.jpg"
}
```

Если пользователь является админом, он может отредактировать личные данные других
зарегистрированных пользователей сайта, направив PATCH- или PUT-запрос 
на эндпойнт /api/users/{id}/, например, /api/users/7/.

#### Удаление пользователем своего аккаунта

Авторизованный пользователь может удалить свой собственный аккаунт,
направив DELETE-запрос без передачи каких-либо полей на эндпойнт /api/users/me/

Пример ответа на DELETE-запрос пользователя на удаление своего аккаунта:
```
{
  "id": 7,
  "username": "testuseruser",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "city": "Moscow",
  "birth_date": "11.11.2011",
  "addresses": [
    {
      "id": 7,
      "address": "string",
      "priority_address": true
    }
  ],
  "address_quantity": 1,
  "phone_number": "71177748879",
  "photo": "/media/default.jpg",
  "Success": "This object was successfully deleted"
}
```

Если пользователь является админом, он может удалить аккаунт другого зарегистрированного 
пользователя, направив DELETE-запрос на эндпойнт /api/users/{id}/, например, /api/users/7/.

### Эндпойнты для просмотра пользовательских адресов доставки

Данные эндпойнты доступны только админам и принимают только GET-запросы.

Для просмотра всех адресов конкретного зарегистрированного пользователя админу 
нужно направить запрос на эндпойнт /api/users/{id}/addresses/, например, /api/users/2/addresses/.

Пример ответа на GET-запрос на получение одного из адресов конкретного зарегистрированного пользователя:
```
[
  {
    "id": 1,
    "address": "Какой-то адрес",
    "priority_address": true
  },
  {
    "id": 2,
    "address": "ntcn",
    "priority_address": false
  },
  {
    "id": 3,
    "address": "new address",
    "priority_address": false
  },
  {
    "id": 4,
    "address": "string",
    "priority_address": false
  }
]
```

Для просмотра одного из адресов конкретного зарегистрированного пользователя админу 
нужно направить запрос на эндпойнт /api/users/{user_id}/addresses/{id}/, 
например, /api/users/2/addresses/1/.

Пример ответа на GET-запрос на получение всех адресов конкретного зарегистрированного пользователя:
```
{
  "id": 1,
  "address": "Какой-то адрес",
  "priority_address": true
}
```


## Продукты

### Эндпойнты апи для продуктов и связанных с ними сущностей

Эндпойнт для продуктов находится на /api/products/

С ним связаны эндпойнты:
- категорий /api/categories/
- подкатегорий /api/subcategories/
- компонентов /api/components
- тегов /api/tags/
- производителей /api/producers/
- промоакций /api/promotions/
- избранных продуктов /api/favorite-products/

### Просмотр информации о продуктах, их категориях, подкатегориях, тегах, компонентах, производителях и промоакциях

Просмотр информации о продуктах, а также их категориях, подкатегориях, тегах,
компонентах, производителях и промоакциях доступен как авторизованным, так и
неавторизованным пользователям. Для этого нужно отправить POST-запрос на нужный эндпойнт.

Эндпойнт избранных продуктов (/api/favorite-products/) доступен только админам.
Добавлять и удалять продукты из Избранного могут авторизованные пользователи,
об этом написано в одном из следующих разделов.

Во время просмотра продуктов можно воспользоваться следующими фильтрами:
- name (поиск по частичному вхождению в начало и середину названия продукта, без
учета регистра, например, /api/products/?name=аво покажет продукт с названием "Авокадо"),
- category (поиск по slug категории, например, /api/products/?category=fruit),
- subcategory (поиск по slug подкатегории, например, /api/products/?subcategory=apples),
- producer (поиск по slug производителя, например, /api/products/?producer=best-producer),
- components (поиск по slug компонента, например, /api/products/?components=salt),
- tags (поиск по slug тега, например, /api/products/?tags=breakfast),
- promotions (поиск по id промоакции, например, /api/products/?promotions=1),
- discontinued (поиск по полю discontinued с возможными значениями 0 для False и 1 для True,
например, /api/products/?discontinued=1 покажет продукты, снятые с продажи),
- is_favorited (поиск по методу is_favorited с возможными значениями 0 для False и 1 для True,
например, /api/products/?is_favorited=1 покажет продукты, которые у данного авторизованного 
пользователя входят в избранное, а если пользователь не авторизован, то фильтр покажет
все продукты),
- min_price (поиск по минимальной цене, например, /api/products/?min_price=100
покажет все продукты, цена которых начинается со 100 или выше),
- max_price (поиск по максимальной цене, например, /api/products/?max_price=100
покажет все продукты, цена которых ниже 100 или равна 100).

Также во время просмотра списка продуктов работает пагинация с параметрами page и limit.
В параметр limit передается число продуктов на странице, а в параметр page передается
номер страницы.
Например, запрос /api/products/?page=2&limit=3 покажет 2-ю страницу списка продуктов,
на которой будет не более 3 продуктов.

### Создание новых продуктов, категорий, подкатегорий, тегов, компонентов, производителей и промоакций

Создание доступно только админам с помощью POST-запросов на нужные эндпойнты.

Перед созданием нового продукта нужно решить, к каким категории, подкатегории, тегам, производителям
он будет принадлежать, а также какие компоненты будут в него входить.

_**Категория**_

Для создания новой категории нужно передать на эндпойнт /api/categories/ поля category_name
и slug. Если не передать в запросе значение для поля slug, то оно будет автоматически 
сгенерировано из значения в поле category_name.

Пример POST-запроса:
```
{
  "category_name": "фрукты",
  "slug": "fruit"
}
```

Пример ответа:
```
{
  "id": 11,
  "category_name": "фрукты",
  "slug": "fruit"
}
```

_**Подкатегория**_

Для создания новой подкатегории нужно передать на эндпойнт /api/subcategories/ поля
parent_category (указать id категории, к которой принадлежит создаваемая подкатегория),
name и slug.
Если не передать в запросе значение для поля slug, то оно будет автоматически 
сгенерировано из значения в поле name.

Пример POST-запроса:
```
{
  "parent_category": 2,
  "name": "соль",
  "slug": "salt"
}
```

Пример ответа:
```
{
  "id": 9,
  "parent_category": 2,
  "name": "соль",
  "slug": "salt"
}
```

_**Тег**_

Для создания нового тега нужно передать на эндпойнт /api/tags/ поля name и slug.
Если не передать в запросе значение для поля slug, то оно будет автоматически 
сгенерировано из значения в поле name.

Пример POST-запроса:
```
{
  "name": "завтрак",
  "slug": "breakfast"
}
```

Пример ответа:
```
{
  "id": 6,
  "name": "завтрак",
  "slug": "breakfast"
}
```

_**Компонент**_

Для создания нового компонента нужно передать на эндпойнт /api/components/ поля name и slug.
Если не передать в запросе значение для поля slug, то оно будет автоматически 
сгенерировано из значения в поле name.

Пример POST-запроса:
```
{
  "name": "имбирь",
  "slug": "ginger"
}
```

Пример ответа:
```
{
  "id": 22,
  "name": "имбирь",
  "slug": "ginger"
}
```

_**Производитель**_

Для создания нового производителя нужно передать на эндпойнт /api/producers/ поля
name, slug, producer_type (выбор между "company" и "entrepreneur"), description
(необязательное поле) и address.
Если не передать в запросе значение для поля slug, то оно будет автоматически 
сгенерировано из значения в поле name.

Пример POST-запроса:
```
{
  "name": "Самый лучший производитель",
  "slug": "best-producer",
  "producer_type": "company",
  "description": "Best producer ever!",
  "address": "Москва, Земляной вал, д.5"
}
```

Пример ответа:
```
{
  "id": 5,
  "name": "Самый лучший производитель",
  "slug": "best-producer",
  "producer_type": "company",
  "description": "Best producer ever!",
  "address": "Москва, Земляной вал, д.5"
}
```

_**Промоакция**_

Для создания новой промоакции нужно передать на эндпойнт /api/promotions/ поля
promotion_type (выбор между simple, birthday, loyalty_card, expired_soon, present,
two_for_one, multiple_items), name, slug, discount (от 0 до 100 включительно),
conditions (необязательное поле), is_active (по умолчанию true), is_constant (по 
умолчанию false), start_time (необязательное поле, вставить дату и время) и
end_time (необязательное поле, вставить дату и время).
Если не передать в запросе значение для поля slug, то оно будет автоматически 
сгенерировано из значения в поле name.

Пример POST-запроса:
```
{
  "promotion_type": "expired_soon",
  "name": "Скидка 30% на товары с истекающим сроком годности",
  "discount": 30,
  "conditions": "Срок годности заканчивается завтра",
  "is_active": true,
  "is_constant": false,
  "start_time": "2023-11-13T07:06:20.011Z"
}
```

Пример ответа:
```
{
  "id": 3,
  "promotion_type": "expired_soon",
  "name": "Скидка 30% на товары с истекающим сроком годности",
  "discount": 30,
  "conditions": "Срок годности заканчивается завтра",
  "is_active": true,
  "is_constant": false,
  "start_time": "2023-11-13T10:06:20.011000+03:00",
  "end_time": null
}
```

_**Продукт**_

Для создания нового продукта нужно передать на эндпойнт /api/products/ поля:
- name, 
- description (необязательное поле), 
- subcategory (id подкатегории, из нее в процессе создания продукта будет получена категория - parent category для данной подкатегории),
- tags (необязательное поле, в которое передаются в виде списка id тегов),
- discontinued (по умолчанию false, данное поле показывает, снят ли товар нами с продажи),
- producer (указать id производителя продукта),
- measure_unit (выбор между grams, milliliters и items, по умолчанию items),
- amount (положительное число, показывающее количество граммов/миллилитров или штук в единице данного продукта, по умолчанию равно 1),
- price (неотрицательное число),
- components (список id компонентов, из которых состоит данный продукт),
- kcal (количество ккал в 100 г. продукта, неотрицательное число),
- proteins (количество белков в 100 г. продукта, неотрицательное число),
- fats (количество жиров в 100 г. продукта, неотрицательное число),
- carbohydrates (количество углеводов в 100 г. продукта, неотрицательное число)

Фото продукта следует загружать через Админку, чтобы оно попало в нужную папку.

Пример POST-запроса:
```
{
  "name": "Cоль гималайская",
  "description": "Соль и специи",
  "subcategory": 9,
  "tags": [
    6
  ],
  "discontinued": false,
  "producer": 5,
  "measure_unit": "grams",
  "amount": 1000,
  "price": 100,
  "components": [
    9, 22
  ],
  "kcal": 0,
  "proteins": 0,
  "fats": 0,
  "carbohydrates": 0
}
```

Пример ответа:
```
{
  "id": 4,
  "name": "Cоль гималайская",
  "description": "Соль и специи",
  "creation_time": "2023-11-13T10:16:36.059375+03:00",
  "category": 2,
  "subcategory": 9,
  "tags": [
    6
  ],
  "discontinued": false,
  "producer": 5,
  "measure_unit": "grams",
  "amount": 1000,
  "price": 100,
  "final_price": 100,
  "photo": null,
  "components": [
    9,
    22
  ],
  "kcal": 0,
  "proteins": 0,
  "fats": 0,
  "carbohydrates": 0
}
```

### Редактирование продуктов, категорий, подкатегорий, тегов, компонентов, производителей и промоакций

Доступно админам с помощью PATCH-запросов на эндпойнт /api/products/{id}/, например, /api/products/4/.
При редактировании продукта можно применить к нему промоакции (при создании этого нельзя было сделать).
Для этого нужно передать в запросе поле promotions со списком id промоакций.
В настоящее время действует ограничение: у продукта не может быть более 1 промоакции.
Таким же образом можно отредактировать другие поля (кроме поля id, которое устанавливается
автоматически при создании) продуктов, категорий, подкатегорий, тегов, компонентов,
производителей и промоакций. 


Пример PATCH-запроса с добавлением промоакции к продукту:
```
{
  "promotions": [
    3
  ]
}
```

Пример ответа:
```
{
  "id": 4,
  "name": "Cоль гималайская",
  "description": "Соль и специи",
  "creation_time": "2023-11-13T10:16:36.059375+03:00",
  "category": 11,
  "subcategory": 9,
  "tags": [
    6
  ],
  "discontinued": false,
  "producer": 5,
  "measure_unit": "grams",
  "amount": 1000,
  "price": 100,
  "final_price": 70,
  "promotions": [
    3
  ],
  "photo": null,
  "components": [
    9,
    22
  ],
  "kcal": 0,
  "proteins": 0,
  "fats": 0,
  "carbohydrates": 0
}
```

### Удаление продуктов, категорий, подкатегорий, тегов, компонентов, производителей и промоакций

Удаление доступно только админам с помощью DELETE-запросов на нужный эндпойнт.
В случае необходимости снятия продукта с продажи, вместо его удаления следует
поставить в поле discontinued значение True, чтобы данный продукт не отображался
в Каталоге товаров, но при этом не исчез из Истории заказов покупателей.

### Избранные продукты: просмотр, добавление и удаление

Просмотр всех избранных продуктов всех пользователей доступен только админам
с помощью GET-запросов на эндпойнты:
- /api/favorite-products/ (просмотр всего списка),
- /api/favorite-products/{id}/ (просмотр одной записи из списка, указывается именно
id этой записи, а не id пользователя или продукта)

Добавление продукта в избранное доступно авторизованному пользователю.
Для этого требуется отправить POST-запрос на эндпойнт /api/products/{product_id}/favorite/,
в теле запроса при этом писать ничего не нужно.

Пример ответа на POST-запрос на добавление продукта в избранное:
```
{
  "id": 4,
  "user": {
    "username": "admin",
    "email": "test@test.com"
  },
  "product": {
    "name": "авокадо",
    "producer": {
      "producer_name": "Курочкин П. Н."
    }
  }
}
```

Дважды добавить один и тот же продукт в избранное не получится, иначе в ответ придет ошибка
{"errors": "Этот продукт уже есть в вашем списке Избранного."}

Удаление продукта из избранного тоже доступно авторизованному пользователю.
Для этого требуется отправить DELETE-запрос на эндпойнт /api/products/{product_id}/favorite/,
в теле запроса при этом писать ничего не нужно.

Пример ответа на DELETE-запрос на удаление продукта из избранного:
```
{
  "favorite_product_object_id": 4,
  "favorite_product_id": 1,
  "favorite_product_name": "авокадо",
  "user_id": 8,
  "user_username": "admin",
  "Success": "This favorite product object was successfully deleted"
}
```

Удалить из избранного продукт, который не был в него добавлен, не получится, иначе
в ответ придет ошибка {"errors": "Этого продукта не было в вашем списке Избранного."}

## Корзина покупок

### Создание и изменение корзины покупок

Создание и изменение корзины покупок доступно по эндпойнту /api/shopping_cart/
Оно доступно как авторизованному так и анонимному пользователю.
Для создания корзины необходимо отправить на указанный эндпойнт POST-запрос с полем products(id, quantity)

Пример POST-запроса на создание/изменение корзины:
```
{
  "products": [
      {"id": 12, "quantity": 2},
      {"id": 1, "quantity": 2}
  ]
}
```
Пример ответа:
```
{
    "products": [
        {
            "id": 12,
            "name": "Перец болгарский",
            "photo": "images/products/12.jpg",
            "category": "vegetables-and-herbs",
            "quantity": 2,
            "final_price": 120.0,
            "created_at": 1703501460,
            "total_price": 240.0
        },
        {
            "id": 1,
            "name": "Миндаль",
            "photo": "images/products/1.jpg",
            "category": "nuts-dried-fruits",
            "quantity": 2,
            "final_price": 160.0,
            "created_at": 1703501460,
            "total_price": 320.0
        }
    ],
    "count_of_products": 4,
    "total_price": 560.0
}
```

### Удаление продуктов из корзины покупок

Удаление продуктов из корзины покупок доступно по эндпойнту /api/shopping_cart/{product_id}/
Для удаления продукта из корзины покупок необходимо передать в URL id продукта во время DELETE-запроса
на указанный эндпойнт.

### Удаление всех продуктов из корзины покупок

Удаление корзины покупок доступно по эндпойнту /api/shopping_cart/remove_all/ 
Для удаления корзины покупок происходит во время DELETE-запроса
на указанный эндпойнт.

## Заказ

### Создание заказа
Создание заказа доступно по эндпойнту api/order/
Для создания заказа необходимо отправить на указанный эндпойнт POST-запрос с данными:
- Для авторизированного пользователя: payment_method, delivery_method(delivery_point или address), package
- Для анонимного пользователя: user_data(first name, last name, phone number, email), 
payment_method, delivery_method(delivery_point или address_anonimous), package

Пример POST-запроса на создание заказа анонимного пользователя:

```
{
    "user_data": {
        "first_name": "Vasya",
        "last_name": "Kovin",
        "phone_number": "89764563456",
        "email": "user@example.com"
    },
    "payment_method": "Payment at the point of delivery",
    "delivery_method": "Point of delivery",
    "delivery_point": 1,
    "package": 100
}

{
    "user_data": {
        "first_name": "Vasya",
        "last_name": "Kovin",
        "phone_number": "89764563456",
        "email": "user@example.com"
    },
    "payment_method": "In getting by cash",
    "delivery_method": "By courier",
    "package": 100,
    "add_address": "Санкт-Петербург, улица Горохова, д.5, кв. 11"
}
```
Пример ответа:
```
{
    "id": 3,
    "order_number": "3",
    "user_data": {
        "first_name": "Vasya",
        "last_name": "Kovin",
        "phone_number": "89764563456",
        "email": "user@example.ruu"
    },
    "products": [
        {
            "product": {
                "id": 1,
                "name": "Миндаль",
                "measure_unit": "г.",
                "amount": 100,
                "final_price": 160.0,
                "photo": null,
                "category": {
                    "category_name": "Орехи и сухофрукты",
                    "category_slug": "nuts-dried-fruits"
                }
            },
            "quantity": 2
        },
        {
            "product": {
                "id": 12,
                "name": "Перец болгарский",
                "measure_unit": "г.",
                "amount": 1000,
                "final_price": 120.0,
                "photo": null,
                "category": {
                    "category_name": "Овощи",
                    "category_slug": "vegetables"
                }
            },
            "quantity": 2
        }
    ],
    "payment_method": "In getting by cash",
    "delivery_method": "By courier",
    "add_address": "Санкт-Петербург, улица Горохова, д.5, кв. 11",
    "delivery_point": null,
    "package": 0.0,
    "comment": "string",
    "total_price": 280.0,
    "is_paid": false,
    "status": "Ordered",
    "ordering_date": "2023-12-26T11:38:55.422583+03:00"
}
```
Пример POST-запроса на создание заказа авторизированного пользователя:

```
{
    "payment_method": "In getting by cash",
    "delivery_method": "By courier",
    "package": 100,
    "add_address": "Санкт-Петербург, Невский прспект д.18, оф. 3
}
```
Пример ответа:
```
{
    "id": 34,
    "order_number": "34",
    "user": {
        "username": "Kostya.Smirny",
        "first_name": "Константин",
        "last_name": "Смирнов",
        "phone_number": "+79803456745"
    },
    "products": [
        {
         "product": {
             "id": 1,
             "name": "Миндаль",
             "measure_unit": "г.",
             "amount": 100,
             "final_price": 160.0,
             "photo": null,
             "category": {
                "category_name": "Орехи и сухофрукты",
                "category_slug": "nuts-dried-fruits"
             }
         },
             "quantity": 2
        },
    ],
    "payment_method": "In getting by cash",
    "delivery_method": "By courier",
    "address": null,
    "add_address": "str",
    "delivery_point": null,
    "package": 100.0,
    "comment": null,
    "total_price": 160.0,
    "is_paid": false,
    "status": "Ordered",
    "ordering_date": "2023-12-04T10:52:20.324335+03:00"
}
```
### Просмотр созданного заказа

Просмотр заказа доступен всем пользователям по эндпойнту /api/order/{order_id}/
Для просмотра заказа необходимо передать в URL id заказа во время GET-запроса

Просмотр списка всех заказов доступен авторизированному пользователю по эндпойнту /api/order/
во время GET-запроса.

### Удаление заказа

Удаление заказа доступно авторизированному пользователю по эндпойнту /api/order/{order_id}/
Для удаления заказа необходимо передать в URL id заказа во время DELETE-запроса
на указанный эндпойнт. Отмена заказа возможна только если статус заказа:
- Оформлен,
- В обработке,
- Комплектуется
