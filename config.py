"""
Конфигурация приложения
"""

import os
from pathlib import Path

# Загружаем переменные из .env файла если он существует
def load_env_file():
    """Загружает переменные из .env файла"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Загружаем .env файл
load_env_file()

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB в байтах
