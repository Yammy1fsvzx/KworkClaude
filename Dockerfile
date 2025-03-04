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

# Создание необходимых директорий и настройка прав
RUN mkdir -p /app/media /app/static
RUN chown -R root:root /app
RUN chmod -R 755 /app/static /app/media

# Порт
EXPOSE 8000 