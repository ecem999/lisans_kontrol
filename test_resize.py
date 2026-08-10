import os
import cv2
from pyzbar.pyzbar import decode

upload_dir = r"C:\Users\aaaec\OneDrive\Desktop\lisans\uploads"
img_path = os.path.join(upload_dir, "e3875158-6da8-4f2f-9f53-173b380064cc.png")

img = cv2.imread(img_path)

def test_resize(scale):
    print(f"Testing scale {scale}...")
    resized = cv2.resize(img, (0, 0), fx=scale, fy=scale)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    objs = decode(gray)
    if objs:
        print(f"FOUND: {objs[0].data.decode('utf-8')}")
        return True
    return False

for scale in [0.8, 0.5, 0.3, 0.2, 0.1]:
    if test_resize(scale):
        break

# Test blur
print("Testing blur...")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
objs = decode(blurred)
if objs:
    print(f"FOUND with blur: {objs[0].data.decode('utf-8')}")
