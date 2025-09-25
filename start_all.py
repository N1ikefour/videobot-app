#!/usr/bin/env python3
"""
Запуск веб-приложения и Telegram бота одновременно
"""

import asyncio
import multiprocessing
import os
import subprocess
import sys
import time
from pathlib import Path

def start_web():
    """Запуск веб-приложения"""
    print("🌐 Запускаем веб-приложение...")
    port = os.getenv("PORT", "8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", port
    ])

def start_bot():
    """Запуск Telegram бота"""
    print("🤖 Запускаем Telegram бота...")
    time.sleep(5)  # Ждем запуска веб-приложения
    subprocess.run([sys.executable, "start_bot.py"])

def main():
    """Главная функция"""
    print("🚀 Запускаем VideoBot (веб + бот)...")
    print(f"🌍 Окружение: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    
    # Проверяем переменные окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ TELEGRAM_BOT_TOKEN не найден, запускаем только веб-приложение")
        start_web()
        return
    
    print("✅ Все переменные окружения найдены")
    
    # Создаем процессы
    web_process = multiprocessing.Process(target=start_web)
    bot_process = multiprocessing.Process(target=start_bot)
    
    try:
        # Запускаем веб-приложение
        web_process.start()
        print("✅ Веб-приложение запущено")
        
        # Запускаем бота
        bot_process.start()
        print("✅ Telegram бот запущен")
        
        # Ждем завершения процессов
        web_process.join()
        bot_process.join()
        
    except KeyboardInterrupt:
        print("🛑 Остановка сервисов...")
        web_process.terminate()
        bot_process.terminate()
        web_process.join()
        bot_process.join()
        print("✅ Сервисы остановлены")

if __name__ == "__main__":
    main()
