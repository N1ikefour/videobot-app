FROM python:3.12-slim

# Устанавливаем FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p uploads results temp_downloads

# Railway использует Procfile для запуска, поэтому не указываем CMD
# CMD ["python", "main.py"]
