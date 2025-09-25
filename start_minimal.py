#!/usr/bin/env python3
"""
Минимальный запускающий скрипт для Railway
"""

print("🚀 Минимальный скрипт запущен")

import os
print(f"📁 Директория: {os.getcwd()}")

import sys
print(f"🐍 Python: {sys.version}")

try:
    print("📦 Проверяем файлы...")
    files = os.listdir('.')
    print(f"📋 Файлы: {files}")
except Exception as e:
    print(f"❌ Ошибка списка файлов: {e}")

try:
    print("🌐 Запускаем веб-сервер...")
    import subprocess
    import threading
    
    port = os.getenv("PORT", "8000")
    print(f"🌐 Порт: {port}")
    
    # Запускаем uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", port
    ])
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    
    # Если все сломалось, просто ждем
    print("⏳ Ждем...")
    import time
    while True:
        time.sleep(60)
        print("⏳ Все еще работаем...")
