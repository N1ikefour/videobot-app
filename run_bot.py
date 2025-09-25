#!/usr/bin/env python3
"""
Простой запускающий скрипт для Telegram бота
"""

import asyncio
import sys
import os
import time

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from telegram_bot_standalone import main
        print("🚀 Запускаем Telegram бота...")
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        # Не завершаем программу, просто логируем ошибку
        while True:
            time.sleep(60)  # Ждем и не завершаемся
