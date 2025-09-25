import asyncio
import subprocess
from pathlib import Path
from typing import List
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
        temp_path = str(self.temp_dir.absolute())
        os.environ['TMPDIR'] = temp_path
        os.environ['TMP'] = temp_path
        os.environ['TEMP'] = temp_path
        os.environ['TMPDIR'] = temp_path  # Дублируем для надежности
        
        # Дополнительные переменные для Windows
        os.environ['TMPDIR'] = temp_path
        os.environ['TMP'] = temp_path
        os.environ['TEMP'] = temp_path
        
        print(f"🔧 Настроены переменные окружения: TMPDIR={temp_path}")
        
        # Проверяем доступность FFmpeg (отключено для предотвращения создания временных файлов)
        # self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Проверяет доступность FFmpeg в системе"""
        try:
            # Создаем временные переменные окружения для проверки
            env = os.environ.copy()
            env['TMPDIR'] = str(self.temp_dir)
            env['TMP'] = str(self.temp_dir)
            env['TEMP'] = str(self.temp_dir)
            
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10, env=env)
            if result.returncode == 0:
                print("✅ FFmpeg доступен в системе")
            else:
                print("❌ FFmpeg не найден в системе")
        except Exception as e:
            print(f"❌ Ошибка при проверке FFmpeg: {e}")
    
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
            # Создаем простую команду FFmpeg для копирования
            cmd = [
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-c:v', 'libx264',
                '-preset', 'ultrafast',  # Быстрая обработка
                '-crf', '23',  # Качество
                '-c:a', 'copy',  # Просто копируем аудио без перекодирования
                str(output_path)
            ]
            
            print(f"Выполняем копирование: {' '.join(cmd)}")
            
            # Выполняем команду с нашими переменными окружения
            env = os.environ.copy()
            temp_path = str(self.temp_dir.absolute())
            env['TMPDIR'] = temp_path
            env['TMP'] = temp_path
            env['TEMP'] = temp_path
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
            
            if result.returncode == 0:
                print(f"✅ Видео скопировано: {output_path}")
            else:
                print(f"❌ Ошибка FFmpeg при копировании:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                raise Exception(f"FFmpeg copy error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Ошибка при копировании: {e}")
            # В случае ошибки просто копируем файл
            shutil.copy2(input_path, output_path)
            print(f"📁 Файл скопирован через shutil: {output_path}")
    
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
            # Используем только базовые цвета, которые точно поддерживаются
            colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'magenta', 'lime']
            border_color = random.choice(colors)
            
            print(f"Добавляем рамку цвета {border_color} для копии {copy_num}")
            print(f"Входной файл: {input_path}")
            print(f"Выходной файл: {output_path}")
            
            # Пробуем добавить рамку с улучшенной обработкой ошибок
            try:
                # Создаем простую команду FFmpeg для добавления рамки
                cmd = [
                    'ffmpeg', '-y',  # -y для перезаписи файла
                    '-i', str(input_path),
                    '-vf', f'pad=iw+60:ih+60:30:30:{border_color}',
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',  # Быстрая обработка
                    '-crf', '23',  # Качество
                    '-c:a', 'copy',  # Просто копируем аудио без перекодирования
                    str(output_path)
                ]
                
                print(f"Выполняем команду: {' '.join(cmd)}")
                
                # Выполняем команду с нашими переменными окружения
                env = os.environ.copy()
                temp_path = str(self.temp_dir.absolute())
                env['TMPDIR'] = temp_path
                env['TMP'] = temp_path
                env['TEMP'] = temp_path
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
                
                if result.returncode == 0:
                    print(f"✅ Рамка добавлена: {output_path}")
                else:
                    print(f"❌ Ошибка FFmpeg:")
                    print(f"   stdout: {result.stdout}")
                    print(f"   stderr: {result.stderr}")
                    raise Exception(f"FFmpeg error: {result.stderr}")
                    
            except Exception as pad_error:
                print(f"❌ Ошибка при добавлении рамки: {pad_error}")
                
                # Пробуем альтернативный способ - через drawbox
                try:
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', str(input_path),
                        '-vf', f'drawbox=x=0:y=0:w=iw:h=ih:color={border_color}:t=30',
                        '-c:v', 'libx264',
                        '-preset', 'ultrafast',  # Быстрая обработка
                        '-crf', '23',  # Качество
                        '-c:a', 'copy',  # Просто копируем аудио без перекодирования
                        str(output_path)
                    ]
                    
                    print(f"Пробуем альтернативную команду: {' '.join(cmd)}")
                    
                    env = os.environ.copy()
                    temp_path = str(self.temp_dir.absolute())
                    env['TMPDIR'] = temp_path
                    env['TMP'] = temp_path
                    env['TEMP'] = temp_path
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
                    
                    if result.returncode == 0:
                        print(f"✅ Рамка добавлена (альтернативный способ): {output_path}")
                    else:
                        print(f"❌ Альтернативная команда тоже не сработала:")
                        print(f"   stdout: {result.stdout}")
                        print(f"   stderr: {result.stderr}")
                        raise Exception(f"Alternative FFmpeg error: {result.stderr}")
                        
                except Exception as alt_error:
                    print(f"❌ Альтернативный способ тоже не сработал: {alt_error}")
                    # В случае ошибки просто копируем файл
                    shutil.copy2(input_path, output_path)
                    print(f"📁 Файл скопирован без рамки: {output_path}")
            
        except Exception as e:
            print(f"❌ Общая ошибка при добавлении рамки: {e}")
            print("🔄 Пробуем простое копирование файла...")
            # В случае ошибки просто копируем файл
            try:
                shutil.copy2(input_path, output_path)
                print(f"✅ Файл скопирован без рамки: {output_path}")
            except Exception as copy_error:
                print(f"❌ Ошибка при копировании: {copy_error}")
                # Последняя попытка - простое копирование байтов
                try:
                    with open(input_path, 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())
                    print(f"✅ Файл скопирован байтами: {output_path}")
                except Exception as final_error:
                    print(f"❌ Критическая ошибка: {final_error}")
                    raise
    
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
            # Создаем простую команду FFmpeg для сжатия
            cmd = [
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-c:v', 'libx264',
                '-crf', '28',  # качество сжатия (18-28, где 28 - больше сжатие)
                '-preset', 'ultrafast',  # Быстрая обработка
                '-c:a', 'copy',  # Просто копируем аудио без перекодирования
                str(output_path)
            ]
            
            print(f"Выполняем сжатие: {' '.join(cmd)}")
            
            # Выполняем команду с нашими переменными окружения
            env = os.environ.copy()
            temp_path = str(self.temp_dir.absolute())
            env['TMPDIR'] = temp_path
            env['TMP'] = temp_path
            env['TEMP'] = temp_path
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
            
            if result.returncode == 0:
                print(f"✅ Видео сжато: {output_path}")
            else:
                print(f"❌ Ошибка FFmpeg при сжатии:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                raise Exception(f"FFmpeg compression error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Ошибка при сжатии: {e}")
            # В случае ошибки просто копируем файл
            shutil.copy2(input_path, output_path)
            print(f"📁 Файл скопирован без сжатия: {output_path}")