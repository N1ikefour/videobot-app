import asyncio
import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from video_processor import VideoProcessor
import shutil
from config import TELEGRAM_BOT_TOKEN

# Токен бота
BOT_TOKEN = TELEGRAM_BOT_TOKEN

# Отладочная информация
print(f"🔑 Токен бота загружен: {'✅' if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else '❌'}")
if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
    print(f"🔑 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
else:
    print("❌ Токен не найден! Проверьте .env файл")

class VideoBot:
    def __init__(self):
        self.processor = None  # Создаем только когда нужно
        self.processing_users = set()  # Пользователи, которые сейчас обрабатывают видео
    
    def _get_processor(self):
        """Получает процессор видео, создавая его при необходимости"""
        if self.processor is None:
            self.processor = VideoProcessor()
        return self.processor
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
🎬 Добро пожаловать в VideoBot!

Я могу обрабатывать ваши видео:
• Создавать до 3 копий
• Добавлять цветные рамки
• Сжимать видео для уменьшения размера

Просто отправьте мне видео файл (до 50MB) и я обработаю его!

Команды:
/start - Начать работу
/help - Помощь
        """
        await update.message.reply_text(welcome_text)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📋 Как использовать VideoBot:

1. Отправьте видео файл (MP4, AVI, MOV, MKV, WMV, FLV)
2. Выберите параметры обработки:
   • Количество копий (1-3)
   • Добавить рамки (да/нет)
   • Сжать видео (да/нет)
3. Получите обработанные видео

⚠️ Ограничения:
• Максимальный размер: 50MB
• Обработка может занять время
• Видео автоматически удаляются после отправки
        """
        await update.message.reply_text(help_text)
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик видео файлов"""
        user_id = update.effective_user.id
        
        print(f"📹 Получено видео от пользователя {user_id}")
        
        # Проверяем, не обрабатывает ли пользователь уже видео
        if user_id in self.processing_users:
            print(f"⏳ Пользователь {user_id} уже обрабатывает видео")
            await update.message.reply_text("⏳ Пожалуйста, дождитесь завершения текущей обработки!")
            return
        
        # Проверяем размер файла
        video = update.message.video
        print(f"📹 Информация о видео: размер={video.file_size}, длительность={video.duration}")
        
        if video.file_size > 50 * 1024 * 1024:  # 50MB
            print(f"❌ Файл слишком большой: {video.file_size} байт")
            await update.message.reply_text("❌ Размер файла превышает 50MB!")
            return
        
        self.processing_users.add(user_id)
        
        try:
            # Отправляем сообщение о начале обработки
            processing_msg = await update.message.reply_text("🔄 Начинаю обработку видео...")
            
            # Скачиваем видео
            file = await context.bot.get_file(video.file_id)
            
            # Создаем временную папку для пользователя
            temp_dir = Path(f"temp_{user_id}")
            temp_dir.mkdir(exist_ok=True)
            
            input_path = temp_dir / f"input_{video.file_id}.mp4"
            await file.download_to_drive(input_path)
            
            # Создаем клавиатуру для выбора параметров
            keyboard = [
                [InlineKeyboardButton("📊 Копии: 1", callback_data="copies_1")],
                [InlineKeyboardButton("📊 Копии: 2", callback_data="copies_2")],
                [InlineKeyboardButton("📊 Копии: 3", callback_data="copies_3")],
                [InlineKeyboardButton("🖼️ Рамки: ВКЛ", callback_data="frames_on")],
                [InlineKeyboardButton("🖼️ Рамки: ВЫКЛ", callback_data="frames_off")],
                [InlineKeyboardButton("🗜️ Сжатие: ВКЛ", callback_data="compression_on")],
                [InlineKeyboardButton("🗜️ Сжатие: ВЫКЛ", callback_data="compression_off")],
                [InlineKeyboardButton("🚀 Обработать", callback_data=f"process_{video.file_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(
                "⚙️ Выберите параметры обработки:",
                reply_markup=reply_markup
            )
            
            # Сохраняем путь к файлу в контексте
            context.user_data['video_path'] = str(input_path)
            context.user_data['temp_dir'] = str(temp_dir)
            context.user_data['copies'] = 1
            context.user_data['add_frames'] = False
            context.user_data['compression'] = False
            
            print(f"💾 Сохранены данные пользователя {user_id}:")
            print(f"  📁 Путь к видео: {input_path}")
            print(f"  📁 Временная папка: {temp_dir}")
            print(f"  ⚙️ Параметры по умолчанию: копии=1, рамки=False, сжатие=False")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при обработке видео: {str(e)}")
            self.processing_users.discard(user_id)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data.startswith("copies_"):
            copies = int(data.split("_")[1])
            context.user_data['copies'] = copies
            
            # Обновляем кнопку
            keyboard = self._create_keyboard(context.user_data)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            
        elif data.startswith("frames_"):
            add_frames = data.endswith("_on")
            context.user_data['add_frames'] = add_frames
            
            # Обновляем кнопку
            keyboard = self._create_keyboard(context.user_data)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            
        elif data.startswith("compression_"):
            compression = data.endswith("_on")
            context.user_data['compression'] = compression
            
            # Обновляем кнопку
            keyboard = self._create_keyboard(context.user_data)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            
        elif data.startswith("process_"):
            await self._process_video(query, context)
    
    def _create_keyboard(self, user_data):
        """Создает клавиатуру с текущими настройками"""
        copies = user_data.get('copies', 1)
        add_frames = user_data.get('add_frames', False)
        compression = user_data.get('compression', False)
        
        keyboard = []
        
        # Кнопки для выбора количества копий
        copies_buttons = []
        for i in range(1, 4):
            text = f"📊 Копии: {i}"
            if i == copies:
                text += " ✅"
            copies_buttons.append(InlineKeyboardButton(text, callback_data=f"copies_{i}"))
        keyboard.append(copies_buttons)
        
        # Кнопки для рамок
        frames_text = "🖼️ Рамки: ВКЛ" if add_frames else "🖼️ Рамки: ВЫКЛ"
        if add_frames:
            frames_text += " ✅"
        keyboard.append([InlineKeyboardButton(frames_text, callback_data="frames_on" if not add_frames else "frames_off")])
        
        # Кнопки для сжатия
        compression_text = "🗜️ Сжатие: ВКЛ" if compression else "🗜️ Сжатие: ВЫКЛ"
        if compression:
            compression_text += " ✅"
        keyboard.append([InlineKeyboardButton(compression_text, callback_data="compression_on" if not compression else "compression_off")])
        
        # Кнопка обработки
        keyboard.append([InlineKeyboardButton("🚀 Обработать", callback_data="process_go")])
        
        return keyboard
    
    async def _process_video(self, query, context):
        """Обрабатывает видео с выбранными параметрами"""
        user_id = query.from_user.id
        
        print(f"🎬 Начинаем обработку видео для пользователя {user_id}")
        
        try:
            await query.edit_message_text("🔄 Обрабатываю видео...")
            
            video_path = Path(context.user_data['video_path'])
            temp_dir = Path(context.user_data['temp_dir'])
            copies = context.user_data['copies']
            add_frames = context.user_data['add_frames']
            compression = context.user_data['compression']
            
            print(f"📁 Путь к видео: {video_path}")
            print(f"📁 Временная папка: {temp_dir}")
            print(f"⚙️ Параметры: копии={copies}, рамки={add_frames}, сжатие={compression}")
            
            # Создаем папку для результатов
            result_dir = temp_dir / "results"
            result_dir.mkdir(exist_ok=True)
            print(f"📁 Папка результатов: {result_dir}")
            
            # Обрабатываем видео
            print("🔄 Начинаем обработку видео...")
            processor = self._get_processor()
            result_files = await processor.process_video(
                input_path=video_path,
                output_dir=result_dir,
                copies=copies,
                compression=compression,
                add_frames=add_frames
            )
            print(f"✅ Обработка завершена. Получено {len(result_files)} файлов")
            
            # Отправляем обработанные видео
            print(f"📤 Отправляем {len(result_files)} файлов пользователю {user_id}")
            for i, file_path in enumerate(result_files):
                print(f"📤 Отправляем файл {i+1}: {file_path}")
                try:
                    with open(file_path, 'rb') as video_file:
                        await query.message.reply_video(
                            video=video_file,
                            caption=f"📹 Обработанное видео #{i+1}\n"
                                   f"Копий: {copies}\n"
                                   f"Рамки: {'Да' if add_frames else 'Нет'}\n"
                                   f"Сжатие: {'Да' if compression else 'Нет'}"
                        )
                    print(f"✅ Файл {i+1} отправлен успешно")
                except Exception as send_error:
                    print(f"❌ Ошибка при отправке файла {i+1}: {send_error}")
                    await query.message.reply_text(f"❌ Ошибка при отправке видео #{i+1}: {str(send_error)}")
            
            await query.edit_message_text("✅ Видео успешно обработано и отправлено!")
            
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка при обработке: {str(e)}")
        
        finally:
            # Очищаем временные файлы
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            
            self.processing_users.discard(user_id)

def main():
    """Запуск бота"""
    print("🚀 Запускаем Telegram бота...")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("❌ Установите TELEGRAM_BOT_TOKEN в переменных окружения!")
        print("📝 Создайте файл .env с содержимым: TELEGRAM_BOT_TOKEN=ваш_токен_здесь")
        return
    
    try:
        bot = VideoBot()
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("help", bot.help))
        application.add_handler(MessageHandler(filters.VIDEO, bot.handle_video))
        application.add_handler(CallbackQueryHandler(bot.handle_callback))
        
        print("🤖 Telegram бот запущен!")
        print("📱 Отправьте /start боту для начала работы")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("🔍 Проверьте правильность токена и интернет-соединение")

if __name__ == "__main__":
    main()
