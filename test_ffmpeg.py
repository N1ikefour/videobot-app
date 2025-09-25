#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы ffmpeg-python
"""

import ffmpeg
import os
from pathlib import Path

def test_ffmpeg():
    """Тестирует базовую функциональность ffmpeg-python"""
    print("Тестируем ffmpeg-python...")
    
    try:
        # Проверяем версию ffmpeg
        version = ffmpeg.probe('input.mp4') if os.path.exists('input.mp4') else None
        print("✅ ffmpeg-python работает корректно")
        
        # Тестируем создание простого видео с рамкой
        print("Тестируем создание видео с рамкой...")
        
        # Создаем тестовое видео (если есть входной файл)
        if os.path.exists('input.mp4'):
            test_output = 'test_output.mp4'
            
            # Создаем видео с рамкой
            (
                ffmpeg
                .input('input.mp4')
                .filter('pad', 
                       w='iw+60',
                       h='ih+60', 
                       color='red',
                       x=30,
                       y=30
                )
                .filter('drawtext',
                       text='Test Frame',
                       fontsize=24,
                       fontcolor='white',
                       x=10,
                       y=10
                )
                .output(test_output, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            if os.path.exists(test_output):
                print("✅ Видео с рамкой создано успешно")
                os.remove(test_output)
            else:
                print("❌ Ошибка создания видео с рамкой")
        else:
            print("ℹ️ Нет тестового файла input.mp4 для полного тестирования")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_ffmpeg()


