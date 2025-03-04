FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создание директории приложения
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/media
RUN mkdir -p /app/static

# Установка прав
RUN chown -R www-data:www-data /app

# Переключение на непривилегированного пользователя
USER www-data

# Порт
EXPOSE 8000 