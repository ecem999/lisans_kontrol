import cv2
import pytesseract
import re
import os
import logging
from pyzbar.pyzbar import decode
from config import COUNTRIES_CONFIG
from qreader import QReader
from utils.logger import get_logger

# Global olarak QReader modelini bir kez yükle ki her istekte baştan yüklemesin
qreader = None
def get_qreader():
    global qreader
    if qreader is None:
        qreader = QReader()
    return qreader

logger = logging.getLogger(__name__)

# Windows ortamlarında PATH güncellenmesi gecikebileceği için varsayılan yolu garanti altına alıyoruz.
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

class OCRService:
    def __init__(self, tesseract_cmd_path: str = None):
        """
        Tesseract işletim sisteminde kurulu olmalıdır. 
        Windows kullanıcıları için yol belirtmek gerekebilir:
        Örn: tesseract_cmd_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        """
        # Varsayılan yol bırakıldı, istenirse main üzerinden override edilebilir.
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

    def preprocess_image(self, image_path: str):
        """
        Görüntüyü OCR okuması için optimize eder.
        Gri tonlamaya çevirir ve arka plan gürültüsünü temizleyerek metni belirginleştirir.
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Görsel okunamadı, dosya yolunu kontrol edin: {image_path}")
            
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Görsel OpenCV tarafından okunamadı: {image_path}")
        
        # 1. Gri tonlamaya çevir (Renkleri atarak işlem yükünü hafifletir)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Kontrastı artır ve metni siyah, arkayı beyaz yap (Otsu Thresholding)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        return thresh

    def extract_text(self, processed_image) -> str:
        """
        İyileştirilmiş görselden Tesseract motoru ile ham metni çıkarır.
        """
        # spa (İspanyolca), fra (Fransızca), ita (İtalyanca), eng (İngilizce) dil paketleri zorunlu tutuluyor
        custom_config = r'--psm 11'
        try:
            text = pytesseract.image_to_string(processed_image, config=custom_config, lang='spa+fra+ita+eng')
            return text
        except pytesseract.TesseractNotFoundError:
            raise Exception("Tesseract kurulu değil veya PATH'e eklenmemiş.")

    def parse_image(self, image_path: str, country: str = None) -> dict:
        """
        Görseli işler, varsa QR kodu okur, yoksa metni çıkarır ve config.py'deki Regex kurallarına göre sicil numarasını yakalar.
        """
        try:
            # 1. OpenCV ile resmi oku
            if not os.path.exists(image_path):
                raise ValueError(f"Görsel okunamadı, dosya yolunu kontrol edin: {image_path}")
            
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Görsel OpenCV tarafından okunamadı: {image_path}")

            # 2. QR Kod Tespiti (Özellikle İtalya gibi QR destekli ülkeler için)
            try:
                qr_urls_found = []
                
                # Önce en güçlü Yapay Zeka modeli (QReader/YOLO) ile dene
                try:
                    qr_engine = get_qreader()
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    decoded_texts = qr_engine.detect_and_decode(image=rgb_img)
                    if decoded_texts:
                        for text in decoded_texts:
                            if text:
                                qr_urls_found.append(text)
                except Exception as e:
                    logger.warning(f"QReader hatası: {e}")

                # Eğer QReader bulamazsa, eski usul Pyzbar (Thresholding) ile dene
                if not qr_urls_found:
                    gray_for_qr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    decoded_objects = decode(gray_for_qr)
                    
                    if not decoded_objects:
                        thresh_for_qr = cv2.threshold(gray_for_qr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                        decoded_objects = decode(thresh_for_qr)
                        
                    for obj in decoded_objects:
                        qr_urls_found.append(obj.data.decode("utf-8"))
                        
                # Hala bulamadıysa, son çare OpenCV
                if not qr_urls_found:
                    qr_detector = cv2.QRCodeDetector()
                    url, bbox, _ = qr_detector.detectAndDecode(img)
                    if url:
                        qr_urls_found.append(url)
                        
                for url in qr_urls_found:
                    logger.info(f"QR Kod OKUNDU: {url}")
                    
                    # İtalya için herhangi bir QR kod bulursak (link içeriyorsa) bypass yapalım
                    if country and country.lower() == "italy" and url.startswith("http"):
                        return {
                            "status": "SUCCESS",
                            "guide_data": {
                                "name": "QR Okundu",
                                "license_no": "QR_BYPASS",
                                "country": "italy",
                                "document_type": "official",
                                "qr_url": url
                            }
                        }
            except Exception as e:
                logger.warning(f"QR tarama hatası (Göz ardı ediliyor): {e}")

            # 3. Eğer QR bulunamadıysa (veya İtalya değilse), normal Tesseract OCR işlemine devam et
            processed_img = self.preprocess_image(image_path)
            raw_text = self.extract_text(processed_img)
            
            # Satır sonlarını boşlukla değiştirerek tek parça bir metin haline getiriyoruz
            cleaned_text = " ".join(raw_text.split())
            
            # İsmi Bulma (Satırları gez, "Nombre" kelimesini bulursan bir sonraki dolu satırı isim olarak al)
            extracted_name = "Görselden Algılandı"
            lines = raw_text.split('\n')
            for i, line in enumerate(lines):
                if "NOMBRE" in line.upper():
                    for next_line in lines[i+1:]:
                        if next_line.strip():
                            extracted_name = next_line.strip()
                            break
                    break
            
            # HATA AYIKLAMA (DEBUG): Tesseract'ın ne gördüğünü backend terminaline yazdır
            print("--- OCR HAM ÇIKTISI ---")
            print(raw_text)
            print("-----------------------")
            
            # 3. Metni Temizle: Tesseract araya boşluk veya satır atlaması koysa bile (Örn: "CLM\n 1 23") onları silip büyük harfe çevir
            clean_text_for_regex = raw_text.replace(" ", "").replace("\n", "").upper()
            
            logger.debug(f"OCR'dan çıkarılan temizlenmiş metin: {cleaned_text[:150]}...")
            
            # WFTGA kartı tespiti (Bonus kontrol)
            if "WFTGA" in cleaned_text.upper() or "CULTOUR" in cleaned_text.upper():
                return {
                    "status": "SUCCESS",
                    "guide_data": {
                        "name": "Bilinmiyor",
                        "license_no": "NOT_APPLICABLE",
                        "country": country if country else "UNKNOWN",
                        "document_type": "WFTGA"
                    }
                }
                
            if country and country.lower() in COUNTRIES_CONFIG:
                target_countries = [country.lower()]
            else:
                target_countries = list(COUNTRIES_CONFIG.keys())
                
            for c in target_countries:
                data = COUNTRIES_CONFIG[c]
                regex_pattern = data.get("license_format", "")
                if not regex_pattern:
                    continue
                
                # Config'deki regex'ler tam eşleşme (^ ve $) için yazılmış olabilir.
                # Metin içinde herhangi bir yerde bulabilmek için baş ve sondaki kısıtlamaları kaldırıyoruz.
                search_pattern = regex_pattern.lstrip('^').rstrip('$')
                
                # Taranan metin içinde ilgili formatta bir numara var mı?
                match = re.search(search_pattern, clean_text_for_regex, re.IGNORECASE)
                
                if match:
                    return {
                        "status": "SUCCESS",
                        "guide_data": {
                            "name": extracted_name,
                            "license_no": match.group(0).upper(),
                            "country": c,
                            "document_type": "OCR_IMAGE"
                        }
                    }

            return {
                "status": "NOT_FOUND",
                "message": "Görselde desteklenen formatta bir devlet lisans numarası tespit edilemedi."
            }

        except Exception as e:
            logger.error(f"Görsel işlenirken hata oluştu: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Görsel işlenirken hata oluştu: {str(e)}"
            }
