import pandas as pd
import unicodedata
import re
import os
from utils.logger import get_logger

logger = get_logger(__name__)

EXCEL_FILES = {
    "spain": "data/ispanya.xlsx",
    "france": "data/fransa.xlsx",
    "italy": "data/italya.xlsx"
}

def normalize_text(text: str) -> str:
    """
    Metni HTML artıklarından, aksanlardan, İspanyolca/Türkçe karakterlerden 
    ve gereksiz boşluklardan temizler. Saf, küçük harfli bir string döner.
    """
    if not isinstance(text, str) or not text:
        return ""
    # 1. Aksanları kaldır (á -> a, ñ -> n vb.)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # 2. Harf ve rakam olmayan her şeyi (noktalama, html artığı) boşluğa çevir
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # 3. Birden fazla boşluğu ve alt satırları (\n) tek bir boşluğa indirge
    return ' '.join(text.lower().split())

async def check_guide_in_excel(country: str, guide_name: str) -> dict:
    if not guide_name or guide_name in ["Bilinmiyor", "Görselden Algılandı"]:
        return {
            "status": "UNKNOWN",
            "message": "İsim okunamadığı için Excel listesi kontrolü yapılamıyor."
        }
        
    country_key = country.lower()
    file_path = EXCEL_FILES.get(country_key)
    
    if not file_path or not os.path.exists(file_path):
        return {
            "status": "UNKNOWN",
            "message": f"{country.capitalize()} için yerel Excel veritabanı bulunamadı."
        }
        
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Excel okunurken hata: {e}")
        return {
            "status": "UNKNOWN",
            "message": "Yerel veritabanı okunamadı."
        }
        
    if "Isim_Soyisim" not in df.columns:
        return {
            "status": "UNKNOWN",
            "message": "Excel dosyasında 'Isim_Soyisim' sütunu bulunamadı."
        }
        
    norm_guide_name = normalize_text(guide_name)
    name_parts = norm_guide_name.split()
    significant_parts = [part for part in name_parts if len(part) > 2]
    
    for index, row in df.iterrows():
        excel_name = row.get("Isim_Soyisim", "")
        norm_excel_name = normalize_text(str(excel_name))
        
        # Tam eşleşme (OCR ismi Excel isminde veya tam tersi geçiyorsa)
        exact_match = (norm_guide_name in norm_excel_name) or (norm_excel_name in norm_guide_name)
        
        # Parçalı eşleşme
        all_parts_found = False
        if len(name_parts) > 1 and significant_parts:
             all_parts_found = all(part in norm_excel_name for part in significant_parts)
        
        if exact_match or all_parts_found:
            row_number = index + 2
            
            source_url = row.get("Kaynak_URL", "")
            if pd.isna(source_url) or str(source_url).strip() == "":
                if country_key == "france":
                    source_url = "https://fngic.fr/en/members"
                else:
                    source_url = "Yerel Excel Veritabanı"
                    
            country_display = country.capitalize()
            if country_key == "spain": country_display = "İspanya"
            elif country_key == "france": country_display = "Fransa"
            elif country_key == "italy": country_display = "İtalya"
                    
            return {
                "status": "VALID",
                "message": f"İsim {country_display} Excel listesinde {row_number}. sıradaki isimle uyuşuyor.",
                "url": str(source_url)
            }
            
    return {
        "status": "UNKNOWN",
        "message": "İsim yerel Excel listesinde bulunamadı."
    }
