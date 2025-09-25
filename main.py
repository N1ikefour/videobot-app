from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import shutil
from pathlib import Path
import asyncio
from video_processor import VideoProcessor

app = FastAPI(title="VideoBot App", description="Приложение для обработки видео")

# Создаем директории для загрузок и результатов
UPLOAD_DIR = Path("uploads")
RESULT_DIR = Path("results")
TEMP_DIR = Path("temp_downloads")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Очищаем старые временные файлы при запуске
def cleanup_temp_files():
    """Очищает старые временные файлы"""
    temp_dirs = [TEMP_DIR, Path("temp_processing")]
    
    for temp_dir in temp_dirs:
        try:
            if temp_dir.exists():
                for temp_file in temp_dir.iterdir():
                    if temp_file.is_file():
                        temp_file.unlink()
                        print(f"Удален старый временный файл: {temp_file}")
        except Exception as e:
            print(f"Ошибка при очистке временных файлов из {temp_dir}: {e}")

# Очищаем временные файлы при запуске
cleanup_temp_files()

# Подключаем статические файлы (если папка существует)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

class VideoSettings(BaseModel):
    copies: int = 1
    compression: bool = False
    add_frames: bool = False

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница с формой загрузки видео"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        # Добавляем заголовки для предотвращения кэширования
        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

@app.post("/test-params")
async def test_params(
    compression: str = Form("false"),
    add_frames: str = Form("false")
):
    """Тестовый endpoint для проверки параметров"""
    print(f"🔍 Тест параметров - получено:")
    print(f"  compression: '{compression}' (тип: {type(compression)})")
    print(f"  add_frames: '{add_frames}' (тип: {type(add_frames)})")
    
    compression_bool = compression.lower() in ['true', '1', 'yes', 'on']
    add_frames_bool = add_frames.lower() in ['true', '1', 'yes', 'on']
    
    print(f"🔍 После парсинга:")
    print(f"  compression: {compression_bool}")
    print(f"  add_frames: {add_frames_bool}")
    
    return {
        "received": {
            "compression": compression,
            "add_frames": add_frames
        },
        "parsed": {
            "compression": compression_bool,
            "add_frames": add_frames_bool
        }
    }

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    copies: int = Form(1),
    compression: str = Form("false"),
    add_frames: str = Form("false")
):
    """Обработка загруженного видео"""
    
    # Валидация файла
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Файл должен быть видео")
    
    # Проверка размера файла (50MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 50 * 1024 * 1024:  # 50MB в байтах
        raise HTTPException(status_code=400, detail="Размер файла не должен превышать 50MB")
    
    # Валидация количества копий
    if copies < 1 or copies > 3:
        raise HTTPException(status_code=400, detail="Количество копий должно быть от 1 до 3")
    
    # Преобразуем строки в boolean
    compression_bool = compression.lower() in ['true', '1', 'yes', 'on']
    add_frames_bool = add_frames.lower() in ['true', '1', 'yes', 'on']
    
    print(f"Получены параметры: copies={copies}, compression='{compression}' -> {compression_bool}, add_frames='{add_frames}' -> {add_frames_bool}")
    
    # Создаем уникальный ID для сессии
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    
    # Сохраняем оригинальный файл
    original_path = session_dir / f"original_{file.filename}"
    with open(original_path, "wb") as buffer:
        buffer.write(content)
    
    # Создаем директорию для результатов
    result_session_dir = RESULT_DIR / session_id
    result_session_dir.mkdir(exist_ok=True)
    
    try:
        # Обрабатываем видео
        processor = VideoProcessor()
        result_files = await processor.process_video(
            input_path=original_path,
            output_dir=result_session_dir,
            copies=copies,
            compression=compression_bool,
            add_frames=add_frames_bool
        )
        
        # Удаляем оригинальный загруженный файл
        try:
            original_path.unlink()
            print(f"Удален оригинальный файл: {original_path}")
        except Exception as e:
            print(f"Ошибка при удалении оригинального файла {original_path}: {e}")
        
        # Удаляем папку загрузки если она пустая
        try:
            if session_dir.exists() and not any(session_dir.iterdir()):
                session_dir.rmdir()
                print(f"Удалена пустая папка загрузки: {session_dir}")
        except Exception as e:
            print(f"Ошибка при удалении папки загрузки {session_dir}: {e}")
        
        return {
            "session_id": session_id,
            "message": f"Видео успешно обработано. Создано {len(result_files)} файлов.",
            "files": [f"/download/{session_id}/{file.name}" for file in result_files]
        }
        
    except Exception as e:
        # Очищаем временные файлы в случае ошибки
        shutil.rmtree(session_dir, ignore_errors=True)
        shutil.rmtree(result_session_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки видео: {str(e)}")

@app.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    """Скачивание обработанного файла"""
    file_path = RESULT_DIR / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Создаем временный файл в нашей локальной папке
    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(exist_ok=True)
    
    temp_filename = f"temp_{session_id}_{filename}"
    temp_path = temp_dir / temp_filename
    
    # Копируем файл во временную директорию
    shutil.copy2(file_path, temp_path)
    
    # Удаляем оригинальный файл
    try:
        file_path.unlink()
        print(f"Удален файл: {file_path}")
    except Exception as e:
        print(f"Ошибка при удалении файла {file_path}: {e}")
    
    # Проверяем, остались ли файлы в сессии
    session_dir = RESULT_DIR / session_id
    if session_dir.exists():
        remaining_files = list(session_dir.iterdir())
        if not remaining_files:
            # Если папка пустая, удаляем её
            try:
                session_dir.rmdir()
                print(f"Удалена пустая директория сессии: {session_dir}")
            except Exception as e:
                print(f"Ошибка при удалении директории {session_dir}: {e}")
    
    # Функция для удаления временного файла после скачивания
    def cleanup_temp_file():
        try:
            os.unlink(temp_path)
            print(f"Удален временный файл: {temp_path}")
        except Exception as e:
            print(f"Ошибка при удалении временного файла {temp_path}: {e}")
    
    # Создаем BackgroundTasks и добавляем задачу очистки
    background_tasks = BackgroundTasks()
    background_tasks.add_task(cleanup_temp_file)
    
    return FileResponse(
        path=temp_path,
        filename=filename,
        media_type='application/octet-stream',
        background=background_tasks
    )

@app.delete("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """Очистка временных файлов сессии"""
    upload_path = UPLOAD_DIR / session_id
    result_path = RESULT_DIR / session_id
    
    if upload_path.exists():
        shutil.rmtree(upload_path)
    if result_path.exists():
        shutil.rmtree(result_path)
    
    return {"message": "Файлы сессии удалены"}

@app.post("/cleanup-temp")
async def cleanup_temp():
    """Очистка всех временных файлов"""
    cleanup_temp_files()
    return {"message": "Временные файлы очищены"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Получаем порт из переменной окружения (для деплоя)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

