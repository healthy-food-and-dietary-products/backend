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
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=key
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
