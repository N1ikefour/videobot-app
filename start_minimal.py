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
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    print(f"🌐 Порт: {port}")
    
    # Импортируем приложение
    from main import app
    
    # Запускаем uvicorn напрямую
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
    
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
