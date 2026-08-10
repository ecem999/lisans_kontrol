import requests

BASE_URL = "http://127.0.0.1:8002"

print("--- Test 1: WFTGA Kartı Reddi (Manuel) ---")
res1 = requests.post(f"{BASE_URL}/api/verify/manual", json={
    "country": "spain", 
    "region": "madrid", 
    "document_type": "WFTGA"
})
print("Status:", res1.status_code)
print("Response:", res1.json())
print("\n")


print("--- Test 2: İtalya QR Doğrulaması (Manuel) ---")
res2 = requests.post(f"{BASE_URL}/api/verify/manual", json={
    "country": "italy", 
    "qr_url": "https://www.ministeroturismo.gov.it/verify?id=123", 
    "document_type": "official"
})
print("Status:", res2.status_code)
print("Response:", res2.json())
print("\n")


print("--- Test 3: Hatalı Lisans Formatı (Manuel) ---")
res3 = requests.post(f"{BASE_URL}/api/verify/manual", json={
    "country": "france", 
    "license_no": "12345", 
    "document_type": "official"
})
print("Status:", res3.status_code)
print("Response:", res3.json())
print("\n")


print("--- Test 4: Görsel Yükleme Entegrasyonu (Simülasyon) ---")
# API is expecting a file and form data
# We don't have a real image, but we can send a dummy text file since OCR will just fail gracefully
# Actually, the user wants us to run the tests to show it works.
files = {'file': ('test.jpg', b'dummy content', 'image/jpeg')}
data = {'country': 'spain', 'region': 'andalucia'}
res4 = requests.post(f"{BASE_URL}/api/verify/image", data=data, files=files)
print("Status:", res4.status_code)
print("Response:", res4.json())
print("\n")
