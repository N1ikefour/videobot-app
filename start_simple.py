#!/usr/bin/env python3
"""
Простой запускающий скрипт для Railway
"""

import os
import sys
import subprocess
import threading
import time

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
    except Exception as e:
        print(f"❌ Ошибка веб-приложения: {e}")

def start_bot():
    """Запуск бота"""
    print("🤖 Запускаем бота...")
    time.sleep(3)
    
    try:
        subprocess.run([sys.executable, "run_bot.py"], check=True)
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")

def main():
    """Главная функция"""
    print("🚀 Запуск VideoBot...")
    print(f"📁 Директория: {os.getcwd()}")
    print(f"📦 Файлы: {os.listdir('.')}")
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    print(f"🔑 Токен: {'Есть' if bot_token else 'Нет'}")
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ Запускаем только веб")
        start_web()
        return
    
    # Запускаем в потоках
    web_thread = threading.Thread(target=start_web, daemon=True)
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    
    web_thread.start()
    bot_thread.start()
    
    web_thread.join()
    bot_thread.join()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        # Запускаем хотя бы веб
        try:
            start_web()
        except:
            pass
