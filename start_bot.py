#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота на Railway
"""

import os
import asyncio
import logging
from telegram_bot import main

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == "__main__":
    print("🚀 Запускаем Telegram бота на Railway...")
    
    # Проверяем переменные окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        print("📝 Убедитесь, что токен установлен в Railway Dashboard")
        exit(1)
    
    print(f"✅ Токен найден: {bot_token[:10]}...{bot_token[-5:]}")
    
    try:
        # Запускаем бота
        main()
    except KeyboardInterrupt:
        print("🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        exit(1)
