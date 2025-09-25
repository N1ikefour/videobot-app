#!/usr/bin/env python3
"""
Запуск веб-приложения и Telegram бота одновременно на Railway
"""

import asyncio
import threading
import subprocess
import sys
import os
import time
from pathlib import Path

def start_web():
    """Запуск веб-приложения"""
    print("🌐 Запускаем веб-приложение...")
    port = os.getenv("PORT", "8000")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", port
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска веб-приложения: {e}")
    except KeyboardInterrupt:
        print("🛑 Веб-приложение остановлено")

def start_bot():
    """Запуск Telegram бота"""
    print("🤖 Запускаем Telegram бота...")
    time.sleep(3)  # Ждем запуска веб-приложения
    
    try:
        # Добавляем текущую директорию в путь
        sys.path.insert(0, str(Path(__file__).parent))
        
        from telegram_bot_standalone import main
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    print("🚀 Запускаем VideoBot (веб + бот) на Railway...")
    print(f"🌍 Окружение: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    
    # Проверяем переменные окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ TELEGRAM_BOT_TOKEN не найден, запускаем только веб-приложение")
        start_web()
        return
    
    print("✅ Все переменные окружения найдены")
    
    # Создаем потоки
    web_thread = threading.Thread(target=start_web, daemon=True)
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    
    try:
        # Запускаем веб-приложение
        web_thread.start()
        print("✅ Веб-приложение запущено")
        
        # Запускаем бота
        bot_thread.start()
        print("✅ Telegram бот запущен")
        
        # Ждем завершения потоков
        web_thread.join()
        bot_thread.join()
        
    except KeyboardInterrupt:
        print("🛑 Остановка сервисов...")
        print("✅ Сервисы остановлены")

if __name__ == "__main__":
    main()
