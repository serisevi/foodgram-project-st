#!/bin/bash

# Входим в аккаунт Docker Hub
echo "Вход в Docker Hub..."
echo "Введите ваш пароль Docker Hub:"
docker login -u serisevi

# Устанавливаем версию (тег)
VERSION=${1:-latest}
echo "Версия тегов: $VERSION"

# Сборка образов
echo "Сборка образов..."
docker-compose build

# Тегирование образов для Docker Hub
echo "Тегирование образов..."
docker tag foodgram-project-react_backend serisevi/foodgram-backend:$VERSION
docker tag foodgram-project-react_frontend serisevi/foodgram-frontend:$VERSION
docker tag foodgram-project-react_gateway serisevi/foodgram-nginx:$VERSION

# Отправка образов в Docker Hub
echo "Отправка образов в Docker Hub..."
docker push serisevi/foodgram-backend:$VERSION
docker push serisevi/foodgram-frontend:$VERSION
docker push serisevi/foodgram-nginx:$VERSION

echo "Готово! Образы отправлены в Docker Hub как serisevi/foodgram-*:$VERSION" 