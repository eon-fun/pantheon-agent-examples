FROM python:3.11-slim

# Устанавливаем необходимые пакеты для работы с SQLAlchemy и PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /project

# Устанавливаем PYTHONPATH для видимости зависимостей
ENV PYTHONPATH="/project:/project/simple-ai-tools"

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Указываем команду по умолчанию
CMD ["python", "main.py"]
