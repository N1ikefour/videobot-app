#!/usr/bin/env python3
"""
Wrapper для запуска Telegram бота на Railway
"""

if __name__ == "__main__":
    import asyncio
    import sys
    import os
    
    # Добавляем текущую директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from telegram_bot_standalone import main
        print("🚀 Запускаем Telegram бота через wrapper...")
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
