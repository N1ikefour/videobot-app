#!/usr/bin/env python3
"""
Запуск только Telegram бота (без веб-приложения)
"""

import os
import asyncio
from telegram_bot import main_async

async def main():
    """Запуск только бота"""
    print("🤖 Запускаем только Telegram бота...")
    print(f"🌍 Окружение: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    
    # Проверяем токен
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_BOT_TOKEN не найден!")
        return
    
    print(f"✅ Токен найден: {bot_token[:10]}...{bot_token[-5:]}")
    
    try:
        await main_async()
    except KeyboardInterrupt:
        print("🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
