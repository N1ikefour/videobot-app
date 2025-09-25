#!/usr/bin/env python3
"""
Запуск автономного Telegram бота
"""

import subprocess
import sys
import os

def main():
    """Запуск бота"""
    print("🚀 Запускаем автономный Telegram бот...")
    
    # Проверяем токен
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_BOT_TOKEN не найден!")
        print("🔧 Проверьте переменные окружения в Railway Dashboard")
        return
    
    print(f"✅ Токен найден: {bot_token[:10]}...{bot_token[-5:]}")
    
    try:
        # Запускаем автономный бот
        subprocess.run([sys.executable, "telegram_bot_standalone.py"])
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    main()
