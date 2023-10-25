run:
	cd backend; python3 manage.py runserver

makemig:
	cd backend; python3 manage.py makemigrations

migrate:
	cd backend; python3 manage.py migrate

superuser:
	cd backend; python3 manage.py createsuperuser --email test@test.com --username admin -v 3

shell:
	cd backend; python3 manage.py shell

load_data:
	cd backend; python3 manage.py load_data

dumpdb:
	cd backend; python3 manage.py dumpdata --output dump.json

loaddb:
	cd backend; python3 manage.py loaddata dump.json

collectstatic:
	cd backend; python3 manage.py collectstatic --no-input

up-compose:
	cd infra; sudo docker compose up -d

build-compose:
	cd infra; sudo docker compose up -d --build

stop-compose:
	cd infra; sudo docker compose stop

start-compose:
	cd infra; sudo docker compose start

makemig-compose:
	cd infra; sudo docker compose exec -it web python manage.py makemigrations

migrate-compose:
	cd infra; sudo docker compose exec -it web python manage.py migrate

superuser-compose:
	cd infra; sudo docker compose exec -it web python manage.py createsuperuser --email test@test.com --username admin -v 3
