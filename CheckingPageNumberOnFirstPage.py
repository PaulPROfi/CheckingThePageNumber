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


# Поиск номера страницы в зонах выделенных в define_page_zones
def find_page_number(image_path):
    print(f"Ищем номер страницы в: {image_path}")
    
    # 1. Загружаем картинку
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    print(f" Размер картинки: {width} x {height}")
    
    # 2. Определяем где искать (зоны)
    zones = define_page_zones(width, height)
    
    # 3. Распознаем весь текст на картинке
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    # 4. Ищем подходящие числа в нужных зонах
    for i in range(len(data['text'])):
        text = data['text'][i]
        conf = data['conf'][i]
        x = data['left'][i]
        y = data['top'][i]
        
        # Проверяем подходит ли текст
        is_num, clean_text = is_page_number(text, conf)
        
        if is_num:
            # Проверяем находится ли в нужной зоне
            for zone_name, (x1, y1, x2, y2) in zones.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    print(f"НАЙДЕНО: '{clean_text}' в зоне {zone_name}")
                    return True, clean_text, conf/100
    
    print("Не найдено")
    return False, None, 0

# Преобразование PDF файла в картинку при помощи poppler
def find_page_number_in_pdf(pdf_path):  
    
    try:
        # 1. Превращаем PDF в картинку
        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path= poppler_path)
        if not images:
            print("Не удалось загрузить страницу из PDF")
            return False, None, 
        
        img = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    
        # 2. Сохраняем как временную картинку
        temp_image = "temp_page.png"
        cv2.imwrite(temp_image, img)
        
        # 3. Ищем номер на этой картинке
        result = find_page_number(temp_image)
        
        # 4. Удаляем временный файл
        import os
        os.remove(temp_image)
        
        return result
        
    except Exception as e:
        print(f" Ошибка: {e}")
        return False, None, 0
   
   
   #Для теста работы пока ссылка
result = find_page_number_in_pdf(r"C:\Users\Pavel\Desktop\Разработка\FirstTask\testpdf3.pdf") #ссылка на PDF файл
print(result)