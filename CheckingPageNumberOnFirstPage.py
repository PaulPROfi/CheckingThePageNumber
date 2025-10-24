import pytesseract  # для распознавания текста на картинках
from pdf2image import convert_from_path  # превращает PDF в картинки
import cv2  # работа с изображениями
import re  # для поиска чисел по шаблону
import pandas as pd  # для создания таблиц
import numpy as np  # работа с массивами чисел
import os #работа с файлами
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' #импорт тесеракта
poppler_path=r"C:\poppler\poppler-25.07.0\Library\bin"  #путь к поплеру
folder_with_pdfs = r"C:\Users\Pavel\Desktop\Разработка\FirstTask" # папка с PDF файлами


# Зоны поиска в которых встречаются номера страницы
def define_page_zones(width, height):
    zones = {
        'bottom_right': (int(width * 0.7), int(height * 0.9), width, height),
        'bottom_center': (int(width * 0.3), int(height * 0.9), int(width * 0.7), height),
        'bottom_left': (0, int(height * 0.9), int(width * 0.3), height),
        'top_right': (int(width * 0.7), 0, width, int(height * 0.1))
    }
    return zones

# Проверка являются ли найденные символы номером страницы
def is_page_number(text, confidence):
    clean_text = text.strip()
    
    # Проверяем что текст не пустой и OCR уверен
    if not clean_text or confidence < 30:
        return False, clean_text
    
    # Проверяем что текст короткий (максимум 7 символов)
    if len(clean_text) > 6:
        return False, clean_text
    
    # Проверяем что только цифры и возможно слеш
    if not re.match(r'^\d+/?\d*$', clean_text):
        return False, clean_text
    
    # Фильтруем годы (1900-2100)
    if len(clean_text) == 4:
        try:
            number = int(clean_text)
            if 1900 <= number <= 2100:
                return False, clean_text
        except:
            pass
    
    return True, clean_text

