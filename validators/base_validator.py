from abc import ABC, abstractmethod
import re
from config import COUNTRIES_CONFIG, STATUS_MAP

class BaseValidator(ABC):
    def __init__(self, country_code: str):
        if country_code not in COUNTRIES_CONFIG:
            raise ValueError(f"Desteklenmeyen ülke kodu: {country_code}")
        
        self.config = COUNTRIES_CONFIG[country_code]
        self.country_code = country_code

    def check_wftga_policy(self, document_type: str) -> dict:
        if document_type.upper() == "WFTGA" and not self.config.get("wftga_allowed", False):
            return {
                "status": "INVALID",
                "label": STATUS_MAP["INVALID"]["label"],
                "message": "WFTGA kartı bu ülkede resmi/yasal bir rehberlik lisansı yerine geçmez."
            }
        return {"status": "CONTINUE"}

    def validate_license_format(self, license_no: str) -> bool:
        pattern = self.config.get("license_format", "")
        if not pattern:
            return True
        return bool(re.match(pattern, license_no, re.IGNORECASE))

    @abstractmethod
    async def verify_guide(self, guide_data: dict) -> dict:
        """
        Asenkron doğrulama mantığı (Zorunlu).
        """
        pass
