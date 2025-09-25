#!/usr/bin/env python3
"""
Wrapper для запуска Telegram бота на Railway
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"🔍 Текущая директория: {current_dir}")
print(f"🔍 Содержимое директории: {os.listdir(current_dir)}")

try:
    from telegram_bot_standalone import main
    print("🚀 Запускаем Telegram бота через wrapper...")
    asyncio.run(main())
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
