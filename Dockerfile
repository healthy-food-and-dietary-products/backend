FROM python:3.10-slim
LABEL author='Good Food' version=1
RUN pip install "poetry==1.6.1"
WORKDIR /app
COPY poetry.lock pyproject.toml backend/ /app/
RUN poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-root
CMD ["gunicorn", "good_food.wsgi:application", "--bind", "0:8000"]
