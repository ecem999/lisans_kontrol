import os
import cv2
from pyzbar.pyzbar import decode

upload_dir = r"C:\Users\aaaec\OneDrive\Desktop\lisans\uploads"

for file in os.listdir(upload_dir):
    if file.endswith(".png") or file.endswith(".jpg"):
        img_path = os.path.join(upload_dir, file)
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        print(f"\n--- Dosya: {file} ({os.path.getsize(img_path)} bytes) ---")
        
        # 1. Pyzbar Raw
        try:
            objs = decode(img)
            if objs:
                print(f"  [PyZbar RAW] Bulundu: {[obj.data.decode('utf-8') for obj in objs]}")
            else:
                print("  [PyZbar RAW] Bulunamadı")
        except Exception as e:
            print(f"  [PyZbar RAW] HATA: {e}")

        # 2. Pyzbar Grayscale
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            objs = decode(gray)
            if objs:
                print(f"  [PyZbar GRAY] Bulundu: {[obj.data.decode('utf-8') for obj in objs]}")
            else:
                print("  [PyZbar GRAY] Bulunamadı")
        except Exception as e:
            print(f"  [PyZbar GRAY] HATA: {e}")
            
        # 3. Pyzbar Threshold
        try:
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            objs = decode(thresh)
            if objs:
                print(f"  [PyZbar THRESH] Bulundu: {[obj.data.decode('utf-8') for obj in objs]}")
            else:
                print("  [PyZbar THRESH] Bulunamadı")
        except Exception as e:
            print(f"  [PyZbar THRESH] HATA: {e}")
            
        # 4. OpenCV
        try:
            qr = cv2.QRCodeDetector()
            url, bbox, _ = qr.detectAndDecode(img)
            if url:
                print(f"  [OpenCV RAW] Bulundu: {url}")
            else:
                print("  [OpenCV RAW] Bulunamadı")
        except Exception as e:
            print(f"  [OpenCV RAW] HATA: {e}")
