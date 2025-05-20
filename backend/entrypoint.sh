#!/bin/bash

# Вывод переменных окружения для отладки
echo "Environment variables:"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "DB HOST: db"

# Ждем, пока postgres будет готов к подключению
echo "Waiting for postgres..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "PostgreSQL started"

# Более прямой подход к созданию базы данных
echo "Creating database if not exists..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $POSTGRES_DB;" || echo "Database may already exist"
echo "Database creation attempted"

# Проверяем, существует ли база данных
echo "Checking if database exists..."
if PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -lqt | cut -d \| -f 1 | grep -qw $POSTGRES_DB; then
    echo "Database $POSTGRES_DB exists"
else
    echo "ERROR: Database $POSTGRES_DB does not exist!"
    echo "Trying alternative approach..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -c "CREATE DATABASE foodgram;" || echo "Failed to create database"
fi

# Создаем миграции
echo "Making migrations..."
python manage.py makemigrations --noinput

# Применяем миграции
echo "Applying migrations..."
python manage.py migrate --noinput

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Создаем суперпользователя
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='admin@foodgram.ru').exists():
    User.objects.create_superuser(
        email='admin@foodgram.ru',
        username='admin',
        password='Test@12345',
        first_name='Администратор',
        last_name='Foodgram'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Запускаем сервер
echo "Starting server..."
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 