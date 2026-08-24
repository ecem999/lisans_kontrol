FROM python:3.12-slim

# Sistem bağımlılıklarını kur: Tesseract OCR + Türkçe/İspanyolca dil paketleri + OpenCV için gerekli kütüphaneler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-ita \
    tesseract-ocr-tur \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Önce bağımlılıkları kopyala ve kur (Docker layer cache için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Vercel ile ilgili gereksiz dosyaları temizle
# Railway 8000 portunu kullanır
EXPOSE 8000

# Sunucuyu başlat
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
