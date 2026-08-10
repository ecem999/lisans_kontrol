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
        from playwright.async_api import async_playwright
        
        url = "https://fngic.fr/en/members"
        
        # Öncelik isimde, yoksa lisans numarasını arama terimi olarak kullanalım.
        search_term = guide_data.get("name")
        if not search_term or search_term in ["Bilinmiyor", "Görselden Algılandı"]:
            search_term = guide_data.get("license_no", "")
            
        if not search_term:
            return {"status": "UNKNOWN", "label": "Eksik Veri", "message": "Arama için lisans numarası veya geçerli bir isim bulunamadı.", "url": url}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=30000)
                
                # Eğer "Advanced research" alanı kapalıysa tıklayıp açmak gerekebilir
                # await page.get_by_text("Advanced research").click()
                
                # "Name" başlığının hemen altındaki input alanını bul ve doldur
                # CSS Selector alternatifi: input[name='name'] veya benzeri bir ID
                await page.locator("label:has-text('Name') + input, input[name='name']").first.fill(search_term)
                
                # Search butonuna tıkla
                await page.get_by_role("button", name="Search").click()
                
                # Sayfanın veya AJAX isteğinin yüklenmesini bekle
                await page.wait_for_load_state("networkidle")
                
                # Sonuçları doğrula
                no_results = await page.locator("text='No results'").is_visible()
                
                if not no_results:
                    return {
                        "status": "VALID",
                        "label": "Sistemden Döndü",
                        "message": "FNGIC sisteminde doğrulandı.",
                        "url": url
                    }
                return {
                    "status": "INVALID",
                    "label": "Sistemden Döndü",
                    "message": "FNGIC sisteminde kayıt bulunamadı.",
                    "url": url
                }
                
            except Exception as e:
                return {
                    "status": "UNKNOWN",
                    "label": "Doğruluğu Kesinleştirilemedi",
                    "message": str(e),
                    "url": url
                }
            finally:
                await browser.close()
