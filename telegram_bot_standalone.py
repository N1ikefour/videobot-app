#!/usr/bin/env python3
"""
Автономный Telegram бот для Railway
"""

import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from video_processor import VideoProcessor
import shutil

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print(f"🔑 Токен бота загружен: {'✅' if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else '❌'}")
if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
    print(f"🔑 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
else:
    print("❌ Токен не найден! Проверьте переменные окружения в Railway")

class VideoBot:
    def __init__(self):
        self.processor = None
        self.processing_users = set()
    
    def _get_processor(self):
        if self.processor is None:
            self.processor = VideoProcessor()
        return self.processor
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "Пользователь"
        
        print(f"📱 Получена команда /start от пользователя {username} (ID: {user_id})")
        
        welcome_text = f"""
🎬 Добро пожаловать в VideoBot, {username}!

Я могу обрабатывать ваши видео:
• Создавать до 3 копий
• Добавлять цветные рамки
• Сжимать видео для уменьшения размера

📱 **Ваш User ID для веб-приложения:**
        """
        
        # Создаем кнопку с User ID для копирования
        keyboard = [
            [InlineKeyboardButton(f"📋 Скопировать ID: {user_id}", callback_data=f"copy_id_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )
        
        # Отправляем дополнительную инструкцию
        instruction_text = f"""
🔗 **Как использовать:**

1. **Скопируйте ваш ID** (кнопка выше)
2. **Откройте веб-приложение** по ссылке
3. **Вставьте ID** в поле "Telegram User ID"
4. **Загрузите видео** и настройте параметры
5. **Получите готовые файлы** прямо в этот чат!

💡 **Ваш ID:** `{user_id}`

Команды:
/start - Начать работу
/help - Помощь
/myid - Показать мой ID
        """
        
        await update.message.reply_text(instruction_text)
    
    async def myid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /myid"""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "Пользователь"
        
        text = f"""
👤 **Информация о пользователе:**

🆔 **User ID:** `{user_id}`
👤 **Имя:** {username}
📱 **Имя пользователя:** @{update.effective_user.username or 'не указано'}

💡 **Скопируйте ваш ID** и вставьте в веб-приложение!
        """
        
        # Создаем кнопку с User ID для копирования
        keyboard = [
            [InlineKeyboardButton(f"📋 Скопировать ID: {user_id}", callback_data=f"copy_id_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📋 Как использовать VideoBot:

1. Отправьте видео файл (MP4, AVI, MOV, MKV, WMV, FLV)
2. Бот обработает видео и отправит результат
3. Используйте веб-приложение для более детальных настроек

⚠️ Ограничения:
• Максимальный размер: 50MB
• Обработка может занять время
• Видео автоматически удаляются после отправки
        """
        await update.message.reply_text(help_text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("copy_id_"):
            user_id = query.data.replace("copy_id_", "")
            await query.edit_message_text(
                f"✅ **ID скопирован!**\n\n"
                f"🆔 Ваш User ID: `{user_id}`\n\n"
                f"💡 Теперь вставьте этот ID в веб-приложение!",
                parse_mode='Markdown'
            )

async def main():
    """Запуск бота"""
    print("🚀 Запускаем Telegram бота...")
    print(f"🌍 Окружение: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("❌ Установите TELEGRAM_BOT_TOKEN в переменных окружения!")
        print("🔧 Проверьте переменные окружения в Railway Dashboard")
        return
    
    try:
        bot = VideoBot()
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("help", bot.help))
        application.add_handler(CommandHandler("myid", bot.myid))
        application.add_handler(MessageHandler(filters.VIDEO, bot.handle_video))
        application.add_handler(CallbackQueryHandler(bot.button_callback))
        
        print("🤖 Telegram бот запущен!")
        print("📱 Отправьте /start боту для начала работы")
        print("🔍 Логи бота будут отображаться здесь...")
        
        # Запускаем бота
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
        # Ждем завершения
        await application.updater.idle()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("🔍 Проверьте правильность токена и интернет-соединение")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
