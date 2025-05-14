# Foodgram - Продуктовый помощник

## Технологии
- Python 3.9
- Django 3.2
- Django REST framework
- PostgreSQL
- Docker
- Nginx

## Развертывание проекта

### 1. Клонирование репозитория
```bash
git clone http://github.com/serisevi/foodgram-st.git
cd foodgram-st
```

### 2. Настройка окружения
Создайте файл `.env` в корневой директории проекта со следующим содержимым:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME='foodgram'
POSTGRES_USER='foodgram_user'
POSTGRES_PASSWORD='foodgram_password'
DB_HOST='db'
DB_PORT=5432
ALLOWED_HOSTS='localhost,127.0.0.1'
DEBUG=True
```

### 3. Запуск Docker контейнеров
```bash
docker-compose up --build -d
```

### 4. Настройка базы данных

Откройте Git Bash и выполните следующие шаги:

1. Подключитесь к PostgreSQL в контейнере:
```bash
docker exec -it foodgram-st-db-1 psql -U foodgram_user
```
> **Примечание**: 
> - При необходимости добавьте в начало команды `winpty`
> - `foodgram-st-db-1` - имя контейнера с базой данных
> - `foodgram_user` - имя пользователя из файла .env

2. Создайте базу данных:
```sql
create database foodgram;
```
> **Примечание**: `foodgram` - имя базы данных из файла .env

3. Проверьте подключение:
```sql
\c foodgram
```
> Для выхода нажмите `CTRL+Z`

### 5. Настройка бэкенда

Откройте Docker Desktop и перейдите в контейнер backend в раздел Exec.

1. Выполните миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

2. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

### 6. Импорт начальных данных

1. Откройте админ-панель в браузере:
```
http://localhost/admin
```

2. Войдите используя учетные данные суперпользователя

3. В разделе "Ингредиенты" нажмите кнопку "Импорт" и загрузите список ингредиентов из файла:
```
foodgram-st/data/ingredient.json
```

### 7. Завершение установки

Поздравляем! Сайт успешно развернут и готов к использованию.

## Дополнительная информация

- Для выгрузки на Docker Hub используйте скрипт `docker-push.sh`
- Для тестирования API используйте коллекцию Postman