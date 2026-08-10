import json
import re

config_path = r"C:\Users\aaaec\OneDrive\Desktop\lisans\config.py"

with open(config_path, "r", encoding="utf-8") as f:
    content = f.read()

new_config = """COUNTRIES_CONFIG = {
    "france": {
        "license_format": r"^CG-\\d{7}-\\d{1}$",
        "wftga_allowed": False,
        "search_method": "siret_and_registry",
        "reference_image": "assets/training_images/fransa/idcard-anverese.jpeg",
        "base_url": {
            "national": "https://data.inpi.fr/recherche"
        },
        "selectors": {
            "input": "input[placeholder='Siren, Siret, Nom...']",
            "submit": "button.search-btn",
            "success_element": ".results-found-badge",
            "error_element": ".no-results-message"
        }
    },
    "italy": {
        "license_format": r"^[A-Z0-9]{8,12}$",
        "wftga_allowed": False,
        "reference_image": "assets/training_images/id_italy.jpg",
        "base_url": {
            "national": "https://www.ministeroturismo.gov.it/elenco-nazionale"
        },
        "selectors": {
            "input": "input[name='codice_fiscale_o_licenza']",
            "submit": "button#cerca-btn",
            "success_element": "table.elenco-guide tbody tr",
            "error_element": "div.alert-warning:contains('Nessun risultato')"
        }
    },
    "spain": {
        "license_format": r"^(GT|CE|GI|APIT|RG)-?\\d{3,6}-?[A-Z]{0,2}$", 
        "search_method": "region_specific",
        "wftga_allowed": False,
        "regions": {
            "andalucia": {
                "name": "Endülüs (Andalucía)",
                "issuer": "Junta de Andalucía",
                "features": "Genellikle yeşil/beyaz renkli fiziksel yaka kartı. Formatı: GT-XXXX.",
                "reference_image": "assets/training_images/ispanya/andalucia.jpg",
                "url": "https://www.juntadeandalucia.es/turismo/registro",
                "search_method": "portal_search",
                "selectors": { "input": "input[name='num_licencia']", "submit": "button[type='submit']", "success_element": ".alert-success", "error_element": ".alert-danger" }
            },
            "aragon": {
                "name": "Aragón",
                "issuer": "Gobierno de Aragón",
                "features": "Çift dilli (İspanyolca/Aragonca) ibareler içerebilir.",
                "reference_image": "assets/training_images/ispanya/aragon.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "asturias": {
                "name": "Asturias",
                "issuer": "Principado de Asturias",
                "features": "Asturias turizm logosunu (Paraíso Natural) taşıyan mavi/sarı ağırlıklı kart.",
                "reference_image": "assets/training_images/ispanya/asturias.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "baleares": {
                "name": "Balear Adaları (Baleares)",
                "issuer": "Govern Illes Balears (Ada Konseyleri)",
                "features": "Adalara göre (Mallorca, İbiza vb.) farklı konsey logoları taşır. Format: GT-XXX.",
                "reference_image": "assets/training_images/ispanya/baleares.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "canarias": {
                "name": "Kanarya Adaları (Canarias)",
                "issuer": "Gobierno de Canarias",
                "features": "Üzerinde 7 ada logosu veya ilgili adanın (örn: Tenerife) konsey logosu bulunur.",
                "reference_image": "assets/training_images/ispanya/canarias.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "cantabria": {
                "name": "Cantabria",
                "issuer": "Gobierno de Cantabria",
                "features": "Cantabria hükümetinin kırmızı/beyaz armasını taşıyan yaka kartı.",
                "reference_image": "assets/training_images/ispanya/cantabria.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "castilla_la_mancha": {
                "name": "Kastilya-La Mancha",
                "issuer": "Junta de Comunidades de Castilla-La Mancha",
                "features": "Yeşil logolu, üzerinde 'Guía de Turismo' ibaresi bulunan resmi belge.",
                "reference_image": "assets/training_images/ispanya/castilla-la-mancha.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "castilla_y_leon": {
                "name": "Kastilya ve Leon",
                "issuer": "Junta de Castilla y León",
                "features": "Bordo renkli resmi bölgesel logo ve GT ön eki.",
                "reference_image": "assets/training_images/ispanya/castilla-y-leon.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "catalunya": {
                "name": "Katalonya (Cataluña)",
                "issuer": "Generalitat de Catalunya",
                "features": "Sarı/kırmızı çizgili amblem, 'Guia de Catalunya' ibaresi. Format: GC-XXXX.",
                "reference_image": "assets/training_images/ispanya/cataluna.jpg",
                "url": "https://canalempresa.gencat.cat/ca/integraciodepartamentaltramit/guies_turisme",
                "search_method": "portal_search",
                "selectors": None
            },
            "extremadura": {
                "name": "Extremadura",
                "issuer": "Junta de Extremadura",
                "features": "Yeşil/beyaz tasarım, Extremadura arması.",
                "reference_image": "assets/training_images/ispanya/extremadura.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "galicia": {
                "name": "Galiçya (Galicia)",
                "issuer": "Xunta de Galicia",
                "features": "Galiçyaca 'Guía de Turismo de Galicia' yazar. Mavi logoludur. Format: GT-XXXX.",
                "reference_image": "assets/training_images/ispanya/galicia.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "madrid": {
                "name": "Madrid",
                "issuer": "Comunidad de Madrid",
                "features": "Kırmızı logolu 'Guía de Turismo de la Comunidad de Madrid' kartı.",
                "reference_image": "assets/training_images/ispanya/madrid.jpg",
                "url": "https://gestiona.comunidad.madrid/vntr_publico",
                "search_method": "portal_search",
                "selectors": { "input": "#licencia_input", "submit": "#buscar_btn", "success_element": ".resultado-ok", "error_element": ".resultado-error" }
            },
            "murcia": {
                "name": "Murcia",
                "issuer": "Región de Murcia",
                "features": "'Costa Cálida' veya bölge logosu taşıyan resmi yaka kartı.",
                "reference_image": "assets/training_images/ispanya/murcia.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "navarra": {
                "name": "Navarra",
                "issuer": "Gobierno de Navarra",
                "features": "Navarra armalı, kırmızı ağırlıklı resmi yaka kartı.",
                "reference_image": "assets/training_images/ispanya/patrimonio-nacional.jpg", 
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "pais_vasco": {
                "name": "Bask Bölgesi (País Vasco)",
                "issuer": "Gobierno Vasco",
                "features": "Çift dilli (Baskça ve İspanyolca). Kartta 'Turismo Gidaria' ibaresi yer alır.",
                "reference_image": "assets/training_images/ispanya/euskadi.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "rioja": {
                "name": "La Rioja",
                "issuer": "Gobierno de La Rioja",
                "features": "Kırmızı-sarı renk ağırlıklı, Rioja hükümet logolu kart.",
                "reference_image": "assets/training_images/ispanya/patrimonio-nacional.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            },
            "valencia": {
                "name": "Valensiya (Comunidad Valenciana)",
                "issuer": "Generalitat Valenciana",
                "features": "Mavi logolu, kare kod/çip içerebilen akıllı kart.",
                "reference_image": "assets/training_images/ispanya/valencia.jpg",
                "url": "https://turisme.gva.es/turisme/registro",
                "search_method": "portal_search",
                "selectors": None
            },
            "ceuta_melilla": {
                "name": "Ceuta ve Melilla",
                "issuer": "Ciudad Autónoma de Ceuta/Melilla",
                "features": "İlgili şehrin yerel yönetim amblemini taşıyan daha standart kartlar.",
                "reference_image": "assets/training_images/ispanya/melilla.jpg",
                "url": "TBD",
                "search_method": "portal_search",
                "selectors": None
            }
        }
    }
}"""

content = re.sub(r'COUNTRIES_CONFIG\s*=\s*\{.*?\nSTATUS_MAP', new_config + '\n\nSTATUS_MAP', content, flags=re.DOTALL)

with open(config_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Config updated.")
