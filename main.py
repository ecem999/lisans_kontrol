import json
import argparse
import sys
import asyncio
from typing import Dict, Any

from validators.spain_validator import SpainValidator
from validators.france_validator import FranceValidator
from validators.italy_validator import ItalyValidator
from utils.logger import get_logger
from utils.ocr_service import OCRService

logger = get_logger(__name__)

from validators import ValidatorFactory

async def async_main():
    parser = argparse.ArgumentParser(description="Avrupa Resmi Turist Rehberi Doğrulama Sistemi (Antigravity)")
    parser.add_argument("--image", default="", help="Lisans kartı görseli (OCR için dosya yolu)")
    parser.add_argument("--country", default="", help="Ülke adı (örn: spain, france, italy)")
    parser.add_argument("--region", default="", help="Bölge veya şehir (özellikle İspanya için)")
    parser.add_argument("--name", default="", help="Rehberin ad ve soyadı")
    parser.add_argument("--license", default="", help="Lisans numarası")
    parser.add_argument("--wftga", action="store_true", help="WFTGA veya benzeri uluslararası dernek kartı mı?")
    
    args = parser.parse_args()
    guide_data = {}

    if args.image:
        logger.info("OCR Katmanı çalıştırılıyor...")
        ocr = OCRService()
        result = ocr.parse_image(args.image)
        
        if result["status"] == "SUCCESS":
            guide_data = result["guide_data"]
            logger.info(f"OCR Başarılı: Lisans tespit edildi ({guide_data.get('country')} - {guide_data.get('license_no')})")
            
            if guide_data.get("document_type") == "WFTGA":
                if not guide_data.get("country") or guide_data.get("country") == "UNKNOWN":
                    guide_data["country"] = "spain"
            
            if guide_data.get("country") == "spain":
                print(f"\n[SİSTEM] İspanya lisansı ({guide_data.get('license_no')}) tespit edildi.")
                if sys.stdin and sys.stdin.isatty():
                    region = input("Lütfen İspanya için bölgeyi giriniz (örn: andalucia, madrid): ").strip()
                    guide_data["region"] = region
                else:
                    guide_data["region"] = args.region 
                    
        else:
            logger.error(f"OCR Başarısız: {result.get('message')}")
            return
            
    else:
        if not args.country or not args.license:
            logger.error("--image argümanı verilmediyse --country ve --license zorunludur.")
            return
            
        guide_data = {
            "name": args.name,
            "license_no": args.license,
            "region": args.region,
            "document_type": "WFTGA" if args.wftga else "STANDARD",
            "country": args.country
        }

    country_code = guide_data.get("country", "")
    validator = ValidatorFactory.get_validator(country_code)
    
    if not validator:
        error_result = {
            "status": "INVALID",
            "message": f"Desteklenmeyen ülke: {country_code}"
        }
        print(json.dumps(error_result, indent=4, ensure_ascii=False))
        return

    logger.info(f"Sorgu başlatılıyor: Ülke={country_code}, Lisans={guide_data.get('license_no')}")
    
    # Asenkron çağrı (await)
    final_result = await validator.verify_guide(guide_data)
    final_result["country"] = validator.country_code
    
    print("\n--- SONUÇ ---")
    print(json.dumps(final_result, indent=4, ensure_ascii=False))

def main():
    # Asenkron döngüyü en tepeden başlatıyoruz
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
