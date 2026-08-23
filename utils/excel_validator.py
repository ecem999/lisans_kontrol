import openpyxl
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
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return ' '.join(text.lower().split())

async def check_guide_in_excel(country: str, guide_name: str) -> dict:
    if not guide_name or len(guide_name.strip()) < 3 or guide_name in ["Bilinmiyor", "Görselden Algılandı"]:
        return {
            "status": "UNKNOWN",
            "message": "Kart üzerindeki isim okunamadığı için Excel listesi kontrolü yapılamadı."
        }
        
    country_key = country.lower()
    file_path = EXCEL_FILES.get(country_key)
    
    if not file_path or not os.path.exists(file_path):
        return {
            "status": "UNKNOWN",
            "message": f"{country.capitalize()} için yerel Excel veritabanı bulunamadı."
        }
        
    try:
        # read_only=True ve data_only=True performans artırır
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet = wb.active
        
        # Sütun başlıklarını bulalım
        headers = [cell.value for cell in sheet[1]]
        if "Isim_Soyisim" not in headers:
            return {
                "status": "UNKNOWN",
                "message": "Excel dosyasında 'Isim_Soyisim' sütunu bulunamadı."
            }
            
        name_col_idx = headers.index("Isim_Soyisim")
        url_col_idx = headers.index("Kaynak_URL") if "Kaynak_URL" in headers else -1
        
        norm_guide_name = normalize_text(guide_name)
        name_parts = norm_guide_name.split()
        significant_parts = [part for part in name_parts if len(part) > 2]
        
        logger.info(f"EXCEL_VALIDATOR DEBUG - guide_name: '{guide_name}'")
        logger.info(f"EXCEL_VALIDATOR DEBUG - norm_guide_name: '{norm_guide_name}'")
        logger.info(f"EXCEL_VALIDATOR DEBUG - significant_parts: {significant_parts}")
        
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            excel_name = row[name_col_idx]
            if not excel_name:
                continue
                
            norm_excel_name = normalize_text(str(excel_name))
            
            exact_match = (norm_guide_name in norm_excel_name) or (norm_excel_name in norm_guide_name)
            
            all_parts_found = False
            if len(name_parts) > 1 and significant_parts:
                 excel_parts = norm_excel_name.split()
                 all_parts_found = all(part in excel_parts for part in significant_parts)
            
            if exact_match or all_parts_found:
                source_url = row[url_col_idx] if url_col_idx != -1 else ""
                
                if not source_url or str(source_url).strip() == "" or str(source_url).strip() == "nan":
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
                    "message": f"İsim {country_display} Excel listesinde {row_idx}. sıradaki '{excel_name}' ismi ile uyuşuyor.",
                    "url": str(source_url)
                }
                
        return {
            "status": "UNKNOWN",
            "message": "İsim yerel Excel listesinde bulunamadı."
        }
        
    except Exception as e:
        logger.error(f"Excel okunurken hata: {e}")
        return {
            "status": "UNKNOWN",
            "message": "Yerel veritabanı okunamadı."
        }
    finally:
        if 'wb' in locals():
            wb.close()
