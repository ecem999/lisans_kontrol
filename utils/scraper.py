import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from utils.logger import get_logger

logger = get_logger(__name__)

class AsyncScraper:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def submit_search_form(self, url: str, selectors: dict, search_value: str) -> dict:
        """
        Belirtilen URL'ye gider, config'den gelen CSS seçicilerle formu doldurur ve sonucu okur.
        """
        async with async_playwright() as p:
            logger.info(f"Playwright Chromium başlatılıyor... (Timeout: 15000ms)")
            # Chromium'u başlat (bot tespitini zorlaştırmak için argümanlar eklendi)
            browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            context = await browser.new_context(user_agent=self.user_agent)
            
            # navigator.webdriver bayrağını gizle (Stealth modu)
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = await context.new_page()

            try:
                # 1. Sayfaya git (15 saniye timeout)
                logger.info(f"URL'ye gidiliyor: {url}")
                await page.goto(url, timeout=15000)
                
                # 2. Input alanının yüklenmesini bekle ve değeri yaz
                input_selector = selectors.get("input")
                submit_selector = selectors.get("submit")
                
                logger.info(f"Input alanı aranıyor: {input_selector}")
                await page.wait_for_selector(input_selector, timeout=10000)
                await page.fill(input_selector, search_value)
                
                # 3. Butona tıkla
                if submit_selector:
                    logger.info(f"Submit butonuna tıklanıyor: {submit_selector}")
                    await page.click(submit_selector)
                
                # 4. Sonucun yüklenmesini bekle (Başarı ve Hata durumları için eşzamanlı bekleme)
                success_sel = selectors.get("success_element")
                error_sel = selectors.get("error_element")
                
                if success_sel and error_sel:
                    logger.info("Sonuç sayfası bekleniyor...")
                    try:
                        # İki farklı senaryo için dinleyici oluştur
                        success_task = asyncio.create_task(page.wait_for_selector(success_sel, state="visible", timeout=10000))
                        error_task = asyncio.create_task(page.wait_for_selector(error_sel, state="visible", timeout=10000))
                        
                        # Hangisi önce gerçekleşirse onu al
                        done, pending = await asyncio.wait(
                            [success_task, error_task], 
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        
                        # Gerçekleşmeyen (bekleyen) görevi iptal et ki bellek sızıntısı olmasın
                        for task in pending:
                            task.cancel()
                            
                        if success_task in done and success_task.exception() is None:
                            logger.info("Kayıt bulundu (SUCCESS CSS yakalandı).")
                            return {"status": "VALID", "message": "Rehber sicil kaydı doğrulandı."}
                        elif error_task in done and error_task.exception() is None:
                            logger.info("Kayıt bulunamadı (ERROR CSS yakalandı).")
                            return {"status": "INVALID", "message": "Belirtilen lisans numarasına ait kayıt bulunamadı."}
                            
                    except Exception as e:
                        logger.error(f"Sonuç okunamadı: {e}")
                        return {"status": "UNKNOWN", "message": "Sonuç sayfası okunamadı (Süre aşımı)."}
                    finally:
                        await browser.close()
                else:
                    await page.wait_for_timeout(3000)
                    await browser.close()
                    logger.warning("Sonuç okuma kuralları (CSS) eksik.")
                    return {"status": "UNKNOWN", "message": "Bu bölge için sonuç okuma kuralları eksik."}

            except PlaywrightTimeoutError:
                await browser.close()
                logger.error("Scraper hatası: Siteye erişilemedi veya sayfa yapısı değişti (Timeout).")
                return {"status": "UNKNOWN", "message": "Siteye erişilemedi veya sayfa yapısı değişti."}
            except Exception as e:
                await browser.close()
                logger.error(f"Scraper hatası (Beklenmeyen): {str(e)}")
                return {"status": "UNKNOWN", "message": f"Beklenmeyen hata: {str(e)}"}
