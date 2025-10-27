# CheckingThePageNumber
---
## Description
Python script for checking the page number on the first page of a PDF document
---
## Required Libraries
* Tkinter
* Shutil
* Pytesseract
* Pdf2image
* Cv2
* Re
* Numpy
* Os
---
## How does this work
After selecting a PDF file, its first page is converted into an image. Based on the image's height and width, search zones are created that represent typical locations for page numbers in documents. Once the search zones are defined for this document, Tesseract-OCR processes all text on the first page and checks whether numbers are present in the previously defined zones. If numbers are indeed found, the system then verifies whether these numbers actually represent page numbers. If all checks pass successfully, the output displays: Page number, location zone, and OCR confidence level
