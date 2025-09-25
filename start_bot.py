#!/usr/bin/env python3
"""
Простой запускающий скрипт для Telegram бота на Railway
"""

import sys
import os
import asyncio

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from telegram_bot_standalone import main
    asyncio.run(main())
except Exception as e:
    print(f"❌ Ошибка запуска бота: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
