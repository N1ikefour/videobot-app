import asyncio
import subprocess
from pathlib import Path
from typing import List
import tempfile
import os
import shutil
import random

# Попытка импорта ffmpeg-python
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
    print("ffmpeg-python доступен")
except ImportError:
    FFMPEG_AVAILABLE = False
    print("ffmpeg-python не установлен")

class VideoProcessor:
    """Класс для обработки видео с различными параметрами"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        # Создаем локальную папку для временных файлов
        self.temp_dir = Path("temp_processing")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Настраиваем переменные окружения для FFmpeg
        os.environ['TMPDIR'] = str(self.temp_dir)
        os.environ['TMP'] = str(self.temp_dir) 
        os.environ['TEMP'] = str(self.temp_dir)
    
    async def process_video(
        self,
        input_path: Path,
        output_dir: Path,
        copies: int = 1,
        compression: bool = False,
        add_frames: bool = False
    ) -> List[Path]:
        """
        Обрабатывает видео согласно заданным параметрам
        
        Args:
            input_path: Путь к исходному видео
            output_dir: Директория для сохранения результатов
            copies: Количество копий (1-3)
            compression: Включить сжатие
            add_frames: Добавить рамки для уникализации
        
        Returns:
            Список путей к обработанным файлам
        """
        print(f"Начинаем обработку видео: {input_path}")
        print(f"Параметры: копии={copies}, сжатие={compression}, рамки={add_frames}")
        print(f"FFmpeg доступен: {FFMPEG_AVAILABLE}")
        
        result_files = []
        
        for i in range(copies):
            output_filename = f"processed_copy_{i+1}_{input_path.stem}.mp4"
            output_path = output_dir / output_filename
            
            print(f"Обрабатываем копию {i+1}: {output_filename}")
            
            try:
                if add_frames:
                    print(f"Добавляем рамки к копии {i+1}")
                    await self._add_frames_ffmpeg(input_path, output_path, i+1)
                else:
                    print(f"Копируем без рамок копию {i+1}")
                    await self._copy_video_ffmpeg(input_path, output_path)
                
                # Применяем сжатие если нужно
                if compression:
                    print(f"Сжимаем копию {i+1}")
                    compressed_path = output_dir / f"compressed_{output_filename}"
                    await self._compress_video_ffmpeg(output_path, compressed_path)
                    # Заменяем оригинальный файл сжатой версией
                    output_path.unlink()
                    compressed_path.rename(output_path)
                
                result_files.append(output_path)
                print(f"Копия {i+1} готова: {output_path}")
                
            except Exception as e:
                print(f"Ошибка при обработке копии {i+1}: {e}")
                # В случае ошибки просто копируем файл
                shutil.copy2(input_path, output_path)
                result_files.append(output_path)
        
        print(f"Обработка завершена. Создано {len(result_files)} файлов")
        return result_files
    
    async def _copy_video_ffmpeg(self, input_path: Path, output_path: Path):
        """Копирует видео с помощью ffmpeg"""
        if not FFMPEG_AVAILABLE:
            shutil.copy2(input_path, output_path)
            return
            
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._copy_video_ffmpeg_sync, input_path, output_path)
    
    def _copy_video_ffmpeg_sync(self, input_path: Path, output_path: Path):
        """Синхронная версия копирования видео"""
        try:
            (
                ffmpeg
                .input(str(input_path))
                .output(str(output_path), 
                       vcodec='libx264', 
                       acodec='aac', 
                       audio_bitrate='128k',
                       map='0:a')
                .overwrite_output()
                .run(quiet=True)
            )
            print(f"Видео скопировано: {output_path}")
        except Exception as e:
            print(f"Ошибка ffmpeg при копировании: {e}")
            shutil.copy2(input_path, output_path)
    
    async def _add_frames_ffmpeg(self, input_path: Path, output_path: Path, copy_num: int):
        """Добавляет рамки с помощью ffmpeg"""
        if not FFMPEG_AVAILABLE:
            shutil.copy2(input_path, output_path)
            return
            
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._add_frames_ffmpeg_sync, input_path, output_path, copy_num)
    
    def _add_frames_ffmpeg_sync(self, input_path: Path, output_path: Path, copy_num: int):
        """Синхронная версия добавления рамок"""
        try:
            # Генерируем случайный цвет для рамки
            colors = [
                'red', 'green', 'blue', 'yellow', 'purple', 'orange', 
                'pink', 'cyan', 'magenta', 'lime', 'navy', 'maroon'
            ]
            border_color = random.choice(colors)
            
            print(f"Добавляем рамку цвета {border_color} для копии {copy_num}")
            print(f"Входной файл: {input_path}")
            print(f"Выходной файл: {output_path}")
            
            # Сначала пробуем простую рамку без текста
            try:
                (
                    ffmpeg
                    .input(str(input_path))
                    .filter('pad', 
                           w='iw+60',  # ширина + 60px (30px с каждой стороны)
                           h='ih+60',  # высота + 60px (30px сверху и снизу)
                           color=border_color,
                           x=30,       # отступ слева
                           y=30        # отступ сверху
                    )
                    .output(str(output_path), 
                           vcodec='libx264', 
                           acodec='aac', 
                           audio_bitrate='128k',
                           map='0:a')  # Явно копируем аудио поток
                    .overwrite_output()
                    .run(quiet=False)  # Включаем вывод для отладки
                )
                print(f"✅ Рамка добавлена: {output_path}")
                
            except Exception as pad_error:
                print(f"❌ Ошибка при добавлении рамки: {pad_error}")
                
                # Пробуем альтернативный способ - через scale и pad
                try:
                    (
                        ffmpeg
                        .input(str(input_path))
                        .filter('scale', w='iw', h='ih')
                        .filter('pad', 
                               w='iw+60',
                               h='ih+60', 
                               color=border_color,
                               x=30,
                               y=30
                        )
                        .output(str(output_path), 
                               vcodec='libx264', 
                               acodec='aac', 
                               audio_bitrate='128k',
                               map='0:a')
                        .overwrite_output()
                        .run(quiet=False)
                    )
                    print(f"✅ Рамка добавлена (альтернативный способ): {output_path}")
                    
                except Exception as alt_error:
                    print(f"❌ Альтернативный способ тоже не сработал: {alt_error}")
                    # В случае ошибки просто копируем файл
                    shutil.copy2(input_path, output_path)
                    print(f"📁 Файл скопирован без рамки: {output_path}")
            
        except Exception as e:
            print(f"❌ Общая ошибка при добавлении рамки: {e}")
            # В случае ошибки просто копируем файл
            shutil.copy2(input_path, output_path)
            print(f"📁 Файл скопирован без рамки: {output_path}")
    
    async def _compress_video_ffmpeg(self, input_path: Path, output_path: Path):
        """Сжимает видео с помощью ffmpeg"""
        if not FFMPEG_AVAILABLE:
            shutil.copy2(input_path, output_path)
            return
            
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._compress_video_ffmpeg_sync, input_path, output_path)
    
    def _compress_video_ffmpeg_sync(self, input_path: Path, output_path: Path):
        """Синхронная версия сжатия видео"""
        try:
            (
                ffmpeg
                .input(str(input_path))
                .output(str(output_path), 
                       vcodec='libx264',
                       crf=28,  # качество сжатия (18-28, где 28 - больше сжатие)
                       preset='fast',
                       acodec='aac',
                       audio_bitrate='128k'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            print(f"Видео сжато: {output_path}")
        except Exception as e:
            print(f"Ошибка ffmpeg при сжатии: {e}")
            shutil.copy2(input_path, output_path)