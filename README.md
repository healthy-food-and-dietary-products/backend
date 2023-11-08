# good-food

![good_food workflow](https://github.com/healthy-food-and-dietary-products/backend/actions/workflows/good_food_workflow.yaml/badge.svg)

### Локальный запуск приложения в контейнерах

_Важно: при работе в Linux или через терминал WSL2 все команды docker и docker compose нужно выполнять от имени суперпользователя — начинайте их с sudo._

Склонировать репозиторий на свой компьютер и перейти в него:
```
git clone git@github.com:healthy-food-and-dietary-products/backend.git
cd backend
```

Создать в папках infra и backend/good_food файл .env с переменными окружения, необходимыми 
для работы приложения.

Пример содержимого файла:
```
SECRET_KEY=key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EMAIL_HOST_USER=healthyfoodapi@yandex.ru
EMAIL_HOST_PASSWORD=healthyfoodapi@123
MODE=prod
DOCKER=yes
```

Перейти в папку /infra/ и запустить сборку контейнеров с помощью 
docker compose: 
```
cd infra
docker compose up -d
```
После этого будут созданы и запущены в фоновом режиме контейнеры 
(db, web, nginx).

Внутри контейнера web выполнить миграции и создать админа-суперпользователя (для входа 
в админку):
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
После этого Админка должна стать доступна по адресу http://localhost/admin/ .

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

### Создание пользователей

# Создание пользователя доступно по эндоинту /users/
Для создания пользователя необходимо post-запросом отправить следующие обязательные поля:
- email
- username
- password
Помимо этих полей обязательным при регистации пользователя является поле "Город", в котором в настоящий момент автоматически указывается "Москва". 
```

# Аутентификация пользователя доступна по эндпоинту /token/login/
Для аутентификации необходимо post-запросом отправить следующие обязательные поля:
- email
- password

# При обращении аутентифицированного пользователя по эндпоинту /users/me/ доступна информация о пользователе (личный кабинет).


```
### Создание корзины покупок

# Создание корзины покупок доступно по эндоинту /api/users/user_id/shopping_cart/
#  Доступно только зарегистрированному пользователю
#  Для создания корзины покупок необходимо обязательные поля: products(id, quantity)
```
Пример POST запроса на создание корзины:


{
    "products": [
        {"id": "1", "quantity": "9"}, 
        {"id": "3", "quantity": "10"}
        ]
}

```

### Изменение корзины покупок

# Изменение корзины покупок доступно по эндоинту /api/users/user_id/shopping_cart/shopping_cart_id
#  Доступно только зарегистрированному пользователю
#  Для  изменения корзины покупок необходимо id корзины и обязательные поля: products(id, quantity)
```
Пример PATCH запроса на изменение корзины:

{
    "products": [
        {"id": "1", "quantity": "9"}, 
        {"id": "3", "quantity": "1"}
        ]
}

```

### Удаление корзины покупок

# Удаление корзины покупок доступно по эндоинту /api/users/user_id/shopping_cart/shopping_cart_id
#  Доступно только зарегистрированному пользователю
#  Для удаления корзины покупок необходимо id корзины
