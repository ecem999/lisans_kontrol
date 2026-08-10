from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_missing_region():
    # İspanya için bölge eksik HTTP 400 dönecek
    response = client.post(
        "/api/verify",
        json={"name": "Alice", "license_no": "GT-123", "country": "spain", "region": "", "wftga": False}
    )
    print("TEST: Missing Region in /api/verify")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_valid_request():
    # Endülüs bölgesi için doğru request (Playwright çalışacak ve 404 URL'si için UNKNOWN dönecek)
    response = client.post(
        "/api/verify",
        json={"name": "Alice", "license_no": "GT-123", "country": "spain", "region": "andalucia", "wftga": False}
    )
    print("TEST: Valid Request (Playwright Execution) in /api/verify")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    test_missing_region()
    test_valid_request()
