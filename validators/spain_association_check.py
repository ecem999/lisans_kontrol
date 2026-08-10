from playwright.async_api import async_playwright
import unicodedata
import re

# Şehirlere/Bölgelere göre dernek (Whitelist) linkleri
ASSOCIATION_LINKS = {
    "castilla_la_mancha": [
        "https://guiascastillalamancha.com/es/list-of-tourist-guides-in-toledo/",
        "https://guiascastillalamancha.com/es/lista-guias-turisticos-guadalajara-2/",
        "https://guiascastillalamancha.com/es/lista-de-guias-turisticos-de-cuenca/",
        "https://guiascastillalamancha.com/es/lista-de-guias-turisticos-de-ciudad-real/"
    ],
    "asturias": "https://guiasturismoasturias.com/guias-oficiales-de-turismo-en-asturias/",
    "aragon": "https://guiasoficialesturismoaragon.es/busca-tu-guia/",
    "cantabria": "https://apitcantabria.com/en/our-guides/",
    "sevilla": "https://apitsevilla.com/nuestras-guias/",
    "granada": "https://www.agipgranada.com/nuestros-guias/",
    "valencia": "https://guiasoficialescv.com/nuestros-guias/",
}

def normalize_text(text: str) -> str:
    """
    Metni HTML artıklarından, aksanlardan, İspanyolca/Türkçe karakterlerden 
    ve gereksiz boşluklardan temizler. Saf, küçük harfli bir string döner.
    """
    if not text:
        return ""
    # 1. Aksanları kaldır (á -> a, ñ -> n vb.)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # 2. Harf ve rakam olmayan her şeyi (noktalama, html artığı) boşluğa çevir
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # 3. Birden fazla boşluğu ve alt satırları (\n) tek bir boşluğa indirge
    return ' '.join(text.lower().split())

async def check_guide_in_association(region_key: str, guide_name: str) -> dict:
    if not guide_name or guide_name in ["Bilinmiyor", "Görselden Algılandı"]:
        return {
            "status": "UNKNOWN",
            "message": "İsim okunamadığı için dernek listesi kontrolü yapılamıyor."
        }

    urls = ASSOCIATION_LINKS.get(region_key.lower())
    
    if not urls:
         return {"status": "UNKNOWN", "message": "Dernek listesi bulunmuyor."}

    if isinstance(urls, str):
        urls = [urls]

    # Aranacak ismi sterilize et ve kelimelerine (parçalara) ayır
    norm_guide_name = normalize_text(guide_name)
    name_parts = norm_guide_name.split()
    # "de", "la", "el" gibi çok kısa bağlaçları testten çıkar, sadece 2 harften büyük ana isimleri bırak
    significant_parts = [part for part in name_parts if len(part) > 2]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for url in urls:
            try:
                # wait_until="networkidle" -> Tüm ağ trafiği (JS, listeler) yüklenene kadar bekle
                await page.goto(url, wait_until="networkidle", timeout=30000)
                page_text = await page.inner_text("body")
                
                # Sitenin tüm metnini sterilize et
                norm_page_text = normalize_text(page_text)
                
                # Kontrol 1: Bütün isim sırayla sayfada var mı? (Örn: "maria carmen rodriguez")
                if norm_guide_name in norm_page_text:
                    await browser.close()
                    return {
                        "status": "VALID",
                        "message": "Tam isim dernek listesinde doğrulandı.",
                        "url": url
                    }
                
                # Kontrol 2: HTML boşluklarından dolayı bitişik okunamadıysa, parçalı (Fuzzy) kontrol et
                # İsmin tüm anlamlı parçaları o sayfada geçiyor mu?
                if significant_parts and all(part in norm_page_text for part in significant_parts):
                    await browser.close()
                    return {
                        "status": "VALID",
                        "message": "İsim parçaları dernek listesinde başarıyla eşleşti.",
                        "url": url
                    }
                    
            except Exception as e:
                print(f"Tarama atlandı ({url}): {e}")
                continue 
        
        await browser.close()
        return {
            "status": "UNKNOWN",
            "message": "Normalize edilmiş aramalara rağmen isim bulunamadı. Manuel arama gerektirir."
        }
