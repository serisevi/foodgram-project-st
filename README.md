# Foodgram - Продуктовый помощник

## Автор проекта - Минаев Александр Викторович
[ВКонтакте](vk.com/serisevi)
[Телеграмм](t.me/serisevi)

## Стек технологий

- **Backend**:
  - Python 3.9
  - Django 3.2
  - Django REST Framework
  - PostgreSQL
  - Docker

- **Frontend**:
  - React
  - Node.js

- **Инфраструктура**:
  - Nginx 1.25
  - Docker Compose

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

### 4. Импорт начальных данных

1. Откройте [админ-панель](http://localhost/admin) в браузере:

2. Войдите используя учетные данные суперпользователя
```
Данные по умолчанию:
Email: admin@foodgram.ru
Пароль: Test@12345
```

3. В разделе "Ингредиенты" нажмите кнопку "Импорт" и загрузите список ингредиентов из файла:
```
foodgram-st/data/ingredient.json
```

### 5. Завершение установки

Поздравляем! [Сайт](http://localhost/) успешно развернут и готов к использованию.

## Дополнительная информация

1. Для выгрузки на Docker Hub используйте скрипт `docker-push.sh`
2. Для тестирования API используйте коллекцию Postman
3. Для доступа к [документации API](http://localhost/api/docs/) перейдите в папку infra и выполните команду "docker-compose up -d --build", после чего перейдите сюда