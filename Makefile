run:
	cd backend; python3 manage.py runserver

makemig:
	cd backend; python3 manage.py makemigrations

migrate:
	cd backend; python3 manage.py migrate

superuser:
	cd backend; python3 manage.py createsuperuser --email test@test.com --username admin -v 3

superuser-empty:
	cd backend; python3 manage.py createsuperuser

shell:
	cd backend; python3 manage.py shell

load_data:
	cd backend; python3 manage.py load_data

export_data:
	cd backend; python3 manage.py export_data

load_recipes:
	cd backend; python3 manage.py load_recipes

export_recipes:
	cd backend; python3 manage.py export_recipes

dumpdb:
	cd backend; python3 manage.py dumpdata --output dump.json

loaddb:
	cd backend; python3 manage.py loaddata dump.json

collectstatic:
	cd backend; python3 manage.py collectstatic --no-input

up-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml up -d

build-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml up -d --build

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

collectstatic-compose:
	cd infra; sudo docker compose exec -it web python manage.py collectstatic --no-input

shell-compose:
	cd infra; sudo docker compose exec -it web python manage.py shell

ls-compose:
	cd infra; sudo docker compose exec -it web ls

dumpdb-compose:
	cd infra; sudo docker compose exec -it web python manage.py dumpdata --output dump.json

loaddb-compose:
	cd infra; sudo docker compose exec -it web python manage.py loaddata dump.json

load_data-compose:
	cd infra; sudo docker compose exec -it web python manage.py load_data

export_data-compose:
	cd infra; sudo docker compose exec -it web python manage.py export_data

flush-compose:
	cd infra; sudo docker compose exec -it web python manage.py flush

down-all-compose:
	cd infra; sudo docker compose down -v --rmi all

prune-containers:
	sudo docker container prune

prune-images:
	sudo docker image prune

volume-ls:
	sudo docker volume ls

volume-db-rm:
	sudo docker volume rm infra_postgres_value
