#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отправки файлов в Telegram
"""

import asyncio
import httpx
import os
from pathlib import Path
from config import TELEGRAM_BOT_TOKEN

async def test_telegram_send():
    """Тестирует отправку файла в Telegram"""
    print("🧪 Тестируем отправку файла в Telegram...")
    
    # Проверяем токен
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_BOT_TOKEN не настроен!")
        return False
    
    # Проверяем chat_id
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID не настроен!")
        return False
    
    print(f"✅ Токен: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print(f"✅ Chat ID: {chat_id}")
    
    # Создаем тестовый файл
    test_file = Path("test_video.mp4")
    if not test_file.exists():
        print("❌ Тестовый файл test_video.mp4 не найден!")
        print("📝 Создайте тестовый видео файл или используйте существующий")
        return False
    
    try:
        # Читаем файл
        with open(test_file, 'rb') as f:
            video_data = f.read()
        
        print(f"📁 Размер файла: {len(video_data)} байт")
        
        # Отправляем через Telegram Bot API
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        
        files = {
            'video': (test_file.name, video_data, 'video/mp4')
        }
        
        data = {
            'chat_id': chat_id,
            'caption': "🧪 Тестовое видео из приложения"
        }
        
        print("📤 Отправляем файл...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                print("✅ Файл отправлен успешно!")
                return True
            else:
                print(f"❌ Ошибка отправки: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования отправки в Telegram...")
    success = asyncio.run(test_telegram_send())
    
    if success:
        print("✅ Тест завершен успешно!")
        print("📱 Проверьте Telegram - должно прийти тестовое видео")
    else:
        print("❌ Тест завершен с ошибками!")
        print("🔍 Проверьте настройки в .env файле")
