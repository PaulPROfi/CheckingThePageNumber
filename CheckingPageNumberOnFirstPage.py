import tkinter as tk  # для создания диалоговых окон
from tkinter import filedialog, messagebox  # диалог выбора файла и сообщения об ошибках
import shutil  # для поиска исполняемых файлов в PATH
import pytesseract  # для распознавания текста на картинках
from pdf2image import convert_from_path  # превращает PDF в картинки
import cv2  # работа с изображениями
import re  # для поиска чисел по шаблону
import pandas as pd  # для создания таблиц
import numpy as np  # работа с массивами чисел
import os #работа с файлами


def setup_tesseract():
    """
    Настраивает Tesseract
    """
    tesseract_cmd = shutil.which("tesseract") # Ищем tesseract в системной переменной PATH
    
    if tesseract_cmd:
        # Настраиваем путь к tesseract для pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        print(f"✓ Tesseract настроен: {tesseract_cmd}")
        return True
    else:
        print("❌ Tesseract не найден в PATH")
        print("Установите Tesseract-OCR и добавьте в переменную PATH")
        return False

def setup_poppler():
    """
    Находит путь к Poppler для конвертации PDF в изображения
    """    
    # Ищем pdftoppm в системной переменной PATH
    poppler_cmd = shutil.which("pdftoppm")
    if poppler_cmd:
        # Получаем папку, где находится pdftoppm
        poppler_dir = os.path.dirname(poppler_cmd)
        print(f"✓ Poppler найден: {poppler_dir}")
        return poppler_dir
    else:
        print("❌ Poppler не найден в PATH")
        print("Установите Poppler и добавьте папку bin в переменную PATH")
        return None

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
                    messagebox.showinfo("Результат",f"Найден номер страницы: {clean_text}. В зоне: {zone_name}")
                    print(f"НАЙДЕНО: '{clean_text}' в зоне {zone_name}")
                    return True, clean_text, conf/100
    
    messagebox.showinfo("Результат","Номер страницы на первом листе не обнаружен")
    return False, None, 0

# Преобразование PDF файла в картинку при помощи poppler
def find_page_number_in_pdf(pdf_path):  
    
    try:
        # Настраиваем Tesseract для обработки изображений
        if not setup_tesseract():
            messagebox.showerror("Ошибка", "Tesseract не найден!\n\nУстановите Tesseract-OCR и добавьте в PATH.")
            return False, None, 
        
        # Настраиваем Poppler для конвертации PDF
        poppler_path = setup_poppler()
        if not poppler_path:
            messagebox.showerror("Ошибка", "Poppler не найден!\n\nУстановите Poppler и добавьте папку bin в PATH.")
            return False, None, 
        
        # 1. Превращаем PDF в картинку
        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path= poppler_path)
        if not images:
            messagebox.showerror("Ошибка", "Не удалось преобразовать PDF в изображение!")
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
        messagebox.showerror("Ошибка")
        return False, None, 0
   

def Select_PDF_file():
            # Создаем скрытое окно для диалога выбора файла
        root = tk.Tk()
        root.withdraw()  # скрываем главное окно
        
        # Показываем диалог выбора PDF файла
        pdf_path = filedialog.askopenfilename(
            title="Выберите PDF документ для распознавания",
            filetypes=[("PDF файлы", "*.pdf")]
        )
        
        # Проверяем, выбрал ли пользователь файл
        if not pdf_path:
            messagebox.showerror("Ошибка", "PDF файл не выбран")
            return False
        find_page_number_in_pdf(pdf_path)
 
   #Для теста работы пока ссылка
   
Select_PDF_file()
# result = find_page_number_in_pdf(r"C:\Users\Pavel\Desktop\Dev\FirstTask\testpdf1.pdf") #ссылка на PDF файл
# print(result)