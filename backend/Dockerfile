FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir

COPY . .

# Создаем директории для статических файлов
RUN mkdir -p /app/static

# Запускаем сбор статических файлов при старте контейнера
CMD /bin/sh -c "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 foodgram.wsgi"
