#!/usr/bin/env python3
"""
Тестовый скрипт для проверки команд бота
"""

import asyncio
from telegram import Update, User, Chat
from telegram.ext import ContextTypes
from telegram_bot import VideoBot

class MockUser:
    def __init__(self, user_id, username=None):
        self.id = user_id
        self.username = username

class MockMessage:
    def __init__(self, user_id, username=None):
        self.effective_user = MockUser(user_id, username)
        self.text = ""

class MockUpdate:
    def __init__(self, user_id, username=None):
        self.effective_user = MockUser(user_id, username)
        self.message = MockMessage(user_id, username)

class MockContext:
    def __init__(self):
        pass

async def test_bot_commands():
    """Тестирует команды бота"""
    print("🧪 Тестируем команды Telegram бота...")
    
    # Создаем экземпляр бота
    bot = VideoBot()
    
    # Тестовые пользователи
    test_users = [
        (123456789, "testuser1"),
        (987654321, "testuser2"),
        (555666777, None)  # Пользователь без username
    ]
    
    print("\n📱 Тестируем команду /start:")
    for user_id, username in test_users:
        print(f"\n👤 Пользователь: {username or 'Без username'} (ID: {user_id})")
        
        # Создаем мок-объекты
        update = MockUpdate(user_id, username)
        context = MockContext()
        
        try:
            # Тестируем команду start
            await bot.start(update, context)
            print("✅ Команда /start выполнена успешно")
        except Exception as e:
            print(f"❌ Ошибка в команде /start: {e}")
    
    print("\n📱 Тестируем команду /myid:")
    for user_id, username in test_users:
        print(f"\n👤 Пользователь: {username or 'Без username'} (ID: {user_id})")
        
        # Создаем мок-объекты
        update = MockUpdate(user_id, username)
        context = MockContext()
        
        try:
            # Тестируем команду myid
            await bot.myid(update, context)
            print("✅ Команда /myid выполнена успешно")
        except Exception as e:
            print(f"❌ Ошибка в команде /myid: {e}")
    
    print("\n📱 Тестируем команду /help:")
    try:
        update = MockUpdate(123456789, "testuser")
        context = MockContext()
        await bot.help(update, context)
        print("✅ Команда /help выполнена успешно")
    except Exception as e:
        print(f"❌ Ошибка в команде /help: {e}")
    
    print("\n✅ Тестирование команд бота завершено!")

if __name__ == "__main__":
    print("🚀 Запуск тестирования команд бота...")
    asyncio.run(test_bot_commands())
