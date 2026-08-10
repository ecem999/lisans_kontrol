import re
import sys
from validators.base_validator import BaseValidator
from config import STATUS_MAP
from utils.logger import get_logger
from utils.scraper import AsyncScraper

logger = get_logger(__name__)

class SpainValidator(BaseValidator):
    def __init__(self):
        super().__init__("spain")

    # CLI kısmı tamamen kaldırılmıyor, ancak main üzerinden de bölge eksikliği kontrol edilecek.
    def validate_license_format(self, license_no: str) -> bool:
        return super().validate_license_format(license_no)

    async def verify_guide(self, guide_data: dict) -> dict:
        wftga_check = self.check_wftga_policy(guide_data.get("document_type", ""))
        if wftga_check["status"] == "INVALID":
            return wftga_check

        license_no = guide_data.get("license_no", "")
        if not self.validate_license_format(license_no):
             return {
                "status": "INVALID",
                "label": STATUS_MAP["INVALID"]["label"],
                "message": f"Geçersiz lisans formatı. Beklenen format: {self.config['license_format']}"
            }

        region = guide_data.get("region", "").lower()
        
        # REST API yaklaşımı için: Bölge boşsa doğrudan hata (veya UNKNOWN) dönelim.
        # Aslında bu kontrol API katmanında da yapılabilir ama burada da güvenli.
        if not region:
            return {
                "status": "INVALID",
                "label": STATUS_MAP["INVALID"]["label"],
                "message": "İspanya için bölge (region) alanı zorunludur."
            }

        regions_config = self.config.get("regions", {})
        
        if region not in regions_config:
            return {
                "status": "UNKNOWN",
                "label": STATUS_MAP["UNKNOWN"]["label"],
                "message": f"Belirtilen bölge bulunamadı veya desteklenmiyor: {region}"
            }

        region_data = regions_config[region]
        search_method = region_data.get("search_method")
        
        # YEREL EXCEL DOĞRULAMASI
        from utils.excel_validator import check_guide_in_excel
        
        # Excel araması için guide_name'i gönder.
        # İspanya için Excel'de arama yapılırken bölge fark etmez, ama country = 'spain' olmalı
        excel_result = await check_guide_in_excel("spain", guide_data.get("name", ""))
        
        if excel_result["status"] == "VALID":
            return {
                "status": "VALID",
                "label": "Yüksek İhtimalle Doğru",
                "message": excel_result["message"],
                "url": excel_result.get("url")
            }
            
        # Eğer Excel'de bulunamazsa (eski scraping yerine UNKNOWN dönüyoruz)
        return {
            "status": "UNKNOWN",
            "label": STATUS_MAP["UNKNOWN"]["label"],
            "message": excel_result["message"]
        }

    async def _run_portal_scraper(self, region_data: dict, guide_data: dict) -> dict:
        url = region_data.get("url")
        selectors = region_data.get("selectors")
        license_no = guide_data.get("license_no")
        
        # Eğer bu bölge için config'te DOM seçicileri tanımlanmamışsa
        if not selectors:
             return {
                "status": "UNKNOWN",
                "label": "Manuel Kontrol",
                "message": f"{region_data.get('name', 'Bölge')} için online arama yapılandırması eksik."
            }

        logger.info(f"{region_data.get('name', 'Bölge')} için Asenkron Playwright başlatılıyor (URL: {url})")
        scraper = AsyncScraper()
        
        # Asenkron kazıma işlemini başlat
        result = await scraper.submit_search_form(url=url, selectors=selectors, search_value=license_no)
        
        # Scraper'dan dönen duruma göre JSON yanıtını şekillendir
        if result["status"] == "UNKNOWN":
             return {
                "status": "UNKNOWN",
                "label": "Doğruluğu Kesinleştirilemedi",
                "message": result["message"],
                "url": url
            }
            
        return {
            "status": "VALID",
            "label": "Yüksek İhtimalle Doğru",
            "message": "Rehberin kaydı resmi sicilde bulundu.",
            "url": url
        }

    def _check_open_data(self, region_data: dict, guide_data: dict) -> dict:
        return {
            "status": "UNKNOWN",
            "label": STATUS_MAP["UNKNOWN"]["label"],
            "message": "Açık veri dosyası indirme ve tarama işlemi henüz entegre edilmedi."
        }
