import pytesseract
from PIL import Image
import os

print("Test OCR Script Başlatılıyor...")

# Tesseract'ın Windows varsayılan kurulum yolu:
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

try:
    tesseract_version = pytesseract.get_tesseract_version()
    print(f"Başarılı! Tesseract Sürümü: {tesseract_version}")
except Exception as e:
    print("HATA: Tesseract bulunamadı. Yolu kontrol et.")
    print(e)
