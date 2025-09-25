#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы пользователей
"""

import json
from pathlib import Path

def test_user_system():
    """Тестирует систему привязки пользователей к сессиям"""
    print("🧪 Тестируем систему пользователей...")
    
    # Тестовые данные
    test_users = {
        "123456789": "user1_session_001",
        "987654321": "user2_session_002", 
        "555666777": "user3_session_003"
    }
    
    # Создаем тестовый файл
    user_sessions_file = Path("user_sessions.json")
    
    print("📝 Создаем тестовые связи пользователей...")
    with open(user_sessions_file, 'w', encoding='utf-8') as f:
        json.dump(test_users, f, ensure_ascii=False, indent=2)
    
    print("✅ Тестовые данные созданы:")
    for user_id, session_id in test_users.items():
        print(f"  👤 Пользователь {user_id} -> Сессия {session_id}")
    
    # Тестируем загрузку
    print("\n📖 Тестируем загрузку данных...")
    with open(user_sessions_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    print("✅ Данные загружены успешно:")
    for user_id, session_id in loaded_data.items():
        print(f"  👤 Пользователь {user_id} -> Сессия {session_id}")
    
    # Тестируем поиск пользователя
    print("\n🔍 Тестируем поиск пользователей...")
    test_session = "user2_session_002"
    found_user = loaded_data.get(test_session)
    
    if found_user:
        print(f"✅ Найден пользователь {found_user} для сессии {test_session}")
    else:
        print(f"❌ Пользователь для сессии {test_session} не найден")
    
    # Очищаем тестовый файл
    user_sessions_file.unlink()
    print("\n🧹 Тестовый файл удален")
    
    print("\n✅ Тест системы пользователей завершен успешно!")

if __name__ == "__main__":
    test_user_system()
