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

# Импортируем ингредиенты из ingredients.json в таблицу ingredients
echo "Loading ingredients data..."
if [ -f "/app/data/ingredients.json" ]; then
    echo "Found ingredients.json file, loading data into ingredients table..."
    python manage.py shell -c "
import json
from recipes.models import Ingredient
import time

# Подсчитываем количество существующих ингредиентов
existing_count = Ingredient.objects.count()
print(f'Found {existing_count} existing ingredients in database')

if existing_count == 0:
    print('Database is empty. Importing all ingredients...')
    # Загружаем данные из JSON файла
    with open('/app/data/ingredients.json', 'r', encoding='utf-8') as f:
        ingredients_data = json.load(f)

    # Используем bulk_create для быстрого добавления всех ингредиентов
    ingredients_to_create = [
        Ingredient(
            name=item.get('name'),
            measurement_unit=item.get('measurement_unit')
        ) for item in ingredients_data
    ]
    
    Ingredient.objects.bulk_create(ingredients_to_create)
    print(f'Successfully imported {len(ingredients_data)} ingredients into the database')
else:
    print('Database already has ingredients. Importing only missing ingredients...')
    # Загружаем данные из JSON файла
    with open('/app/data/ingredients.json', 'r', encoding='utf-8') as f:
        ingredients_data = json.load(f)

    # Получаем все существующие комбинации имени и единицы измерения
    existing_combinations = set(
        Ingredient.objects.values_list('name', 'measurement_unit')
    )
    
    # Счетчики для статистики
    created_count = 0
    skipped_count = 0
    
    # Создаем только те ингредиенты, которых нет в базе
    for item in ingredients_data:
        name = item.get('name')
        unit = item.get('measurement_unit')
        
        if (name, unit) not in existing_combinations:
            Ingredient.objects.create(name=name, measurement_unit=unit)
            created_count += 1
        else:
            skipped_count += 1
    
    print(f'Results: {created_count} ingredients added, {skipped_count} already existed')
"
    echo "Ingredients loaded successfully into ingredients table"
else
    echo "Warning: /app/data/ingredients.json file not found!"
    # Вывод содержимого каталога для отладки
    echo "Contents of /app/data/ directory:"
    ls -la /app/data/
fi

# Запускаем сервер
echo "Starting server..."
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 