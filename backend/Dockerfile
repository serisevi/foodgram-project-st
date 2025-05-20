FROM python:3.9-slim

WORKDIR /app

# Установка необходимых системных пакетов
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/static/ /app/media/

# Делаем entrypoint.sh исполняемым
RUN chmod +x entrypoint.sh

# Запускаем entrypoint скрипт
ENTRYPOINT ["./entrypoint.sh"]
