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
    time.sleep(5)  # Ждем запуска веб-приложения
    
    try:
        # Добавляем текущую директорию в путь
        sys.path.insert(0, str(Path(__file__).parent))
        
        print("📦 Импортируем модули бота...")
        from telegram_bot_standalone import main
        print("✅ Модули импортированы успешно")
        
        print("🚀 Запускаем асинхронную функцию main...")
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()
        # Не завершаем программу, продолжаем работу веб-сервера

def main():
    """Главная функция"""
    print("🚀 Запускаем VideoBot (веб + бот) на Railway...")
    print(f"🌍 Окружение: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    print(f"📁 Текущая директория: {os.getcwd()}")
    print(f"📦 Содержимое директории: {os.listdir('.')}")
    
    # Проверяем переменные окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    port = os.getenv("PORT", "8000")
    print(f"🔑 BOT_TOKEN найден: {'Да' if bot_token and bot_token != 'YOUR_BOT_TOKEN_HERE' else 'Нет'}")
    print(f"🌐 PORT: {port}")
    
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
        print("⏳ Ждем завершения потоков...")
        web_thread.join()
        bot_thread.join()
        
    except KeyboardInterrupt:
        print("🛑 Остановка сервисов...")
        print("✅ Сервисы остановлены")
    except Exception as e:
        print(f"❌ Критическая ошибка в main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
