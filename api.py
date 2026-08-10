import os
import sys
import uuid
import shutil
import asyncio

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from validators import ValidatorFactory
from utils.ocr_service import OCRService
from utils.visual_matcher import VisualMatcher
from config import COUNTRIES_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Antigravity Avrupa Rehber Doğrulama API",
    description="İspanya, Fransa ve İtalya için turist rehberi lisans doğrulama motoru",
    version="1.0.0"
)

# Initialize VisualMatcher globally
# Not: Yüklediğimiz modül klasör yapısıyla uyuşuyor, referans dosyaları varsayılan dizinde.
matcher = VisualMatcher()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class GuideDataRequest(BaseModel):
    country: str
    region: Optional[str] = None
    license_no: Optional[str] = None
    name: Optional[str] = None
    document_type: Optional[str] = "official" # official, WFTGA, vb.
    qr_url: Optional[str] = None

@app.post("/api/verify/manual")
async def verify_manual(request: GuideDataRequest):
    """Kullanıcının form üzerinden girdiği verilerle doğrulama yapar."""
    country_code = request.country.lower()
    
    try:
        validator = ValidatorFactory.get_validator(country_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if country_code == "spain" and not request.region:
        raise HTTPException(status_code=400, detail={"error": "MISSING_REGION", "message": "İspanya için bölge (region) alanı zorunludur."})

    guide_data = request.dict()

    try:
        result = await validator.verify_guide(guide_data)
        result["country"] = validator.country_code
        return result
    except Exception as e:
        logger.error(f"Doğrulama sırasında hata: {e}")
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")


@app.post("/api/verify/image")
async def verify_image(
    country: str = Form(...),
    region: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """Yüklenen görseli OCR'dan geçirir ve elde edilen verilerle doğrulama yapar."""
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        ocr = OCRService()
        ocr_result = ocr.parse_image(file_path, country=country)
        
        if ocr_result["status"] != "SUCCESS":
            logger.warning(f"OCR Başarısız: {ocr_result}")
            raise HTTPException(status_code=400, detail={"error": "OCR_FAILED", "message": ocr_result.get("message", "Görsel işlenemedi.")})
            
        ocr_extracted_data = ocr_result["guide_data"]
        
        detected_region = None
        match_score = None
        detected_region_name = None
        
        if country.lower() == "spain" and (not region or region == "auto"):
            logger.info("İspanya için otomatik bölge tespiti (Visual Matcher) başlatılıyor...")
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            
            match_result = matcher.match_image(image_bytes)
            
            if match_result["match_found"]:
                res_region = match_result["region"]
                score = match_result["score"]
                # region_name -> 'cataluna' gibi geldiğinden config üzerinden ismini bulalım
                # Eğer config'de birebir eşleşen key yoksa, adını capitalize yapalım.
                # Mesela 'cataluna' dosya adı, config key'i 'catalunya' olabilir. 
                # Ama referans verisinde cataluna_name gibi doğrudan bir map'imiz var.
                # 'aragon.jpg' -> 'aragon' -> 'Aragón'
                # Ancak dosya adı ile config key eşleşmeyebilir (cataluna vs catalunya).
                # Bunun için COUNTRIES_CONFIG'den bulmaya çalışalım.
                name = None
                for key, val in COUNTRIES_CONFIG["spain"]["regions"].items():
                    # Dosya yolu üzerinden eşleştir (ör: "cataluna.jpg" geçiyorsa)
                    if f"{res_region}.jpg" in val.get("reference_image", ""):
                        name = val.get("name")
                        res_region = key # config'deki asıl key'i de alalım
                        break
                if not name:
                    name = res_region.capitalize()
                    
                logger.info(f"Visual Match Başarılı! Bölge: {name} (Score: {score}%, Good Matches: {match_result['matches_count']})")
                region = res_region
                detected_region = res_region
                match_score = score
                detected_region_name = name
            else:
                score = match_result["score"]
                matches_count = match_result.get("matches_count", 0)
                logger.warning(f"Visual Match başarısız veya eşik değerin altında kaldı. (Score: {score}%, Matches: {matches_count})")
                raise HTTPException(status_code=400, detail={"error": "MISSING_REGION", "message": match_result["message"]})
        
        guide_data = {
            "country": country,
            "region": region,
            "license_no": ocr_extracted_data.get("license_no"),
            "name": ocr_extracted_data.get("name"),
            "document_type": ocr_extracted_data.get("document_type", "official"),
            "qr_url": ocr_extracted_data.get("qr_url")
        }
        
        try:
            validator = ValidatorFactory.get_validator(country.lower())
            result = await validator.verify_guide(guide_data)
            result["country"] = validator.country_code
            
            if detected_region:
                result["detected_region"] = detected_region
                result["detected_region_name"] = detected_region_name
                result["match_score"] = match_score
                
            result["ocr_license_found"] = guide_data.get("license_no")
            result["extracted_data"] = guide_data
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR/Doğrulama hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Görsel işleme hatası: {str(e)}")
