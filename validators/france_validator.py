from validators.base_validator import BaseValidator
from config import STATUS_MAP
from utils.scraper import AsyncScraper

class FranceValidator(BaseValidator):
    def __init__(self):
        super().__init__("france")

    async def verify_guide(self, guide_data: dict) -> dict:
        # 1. WFTGA veya benzeri geçersiz kart kontrolü
        wftga_check = self.check_wftga_policy(guide_data.get("document_type", ""))
        if wftga_check["status"] == "INVALID":
            return wftga_check

        # 2. Guide-conférencier format kontrolü (CG-XXXXXXX-X)
        license_no = guide_data.get("license_no", "")
        if not self.validate_license_format(license_no):
            return {
                "status": "INVALID",
                "label": STATUS_MAP["INVALID"]["label"],
                "message": f"Geçersiz Fransa lisans formatı. Beklenen: {self.config['license_format']}"
            }

        # 3. Fransa Merkezi Doğrulama Süreci
        search_method = self.config.get("search_method")
        
        if search_method == "siret_and_registry":
            return await self._check_siret_and_registry(guide_data)
        else:
            return {
                "status": "UNKNOWN",
                "label": STATUS_MAP["UNKNOWN"]["label"],
                "message": "Fransa için yapılandırılmış bir doğrulama metodu bulunamadı."
            }

    async def _check_siret_and_registry(self, guide_data: dict) -> dict:
        from utils.excel_validator import check_guide_in_excel
        
        excel_result = await check_guide_in_excel("france", guide_data.get("name", ""))
        
        if excel_result["status"] == "VALID":
            return {
                "status": "VALID",
                "label": "Sistemden Döndü",
                "message": excel_result["message"],
                "url": excel_result.get("url")
            }
            
        return {
            "status": "UNKNOWN",
            "label": "Eksik Veri",
            "message": excel_result["message"]
        }
