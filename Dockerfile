# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Запускаем команду для старта
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 