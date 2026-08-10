import cv2
import zxingcpp
import os

upload_dir = r"C:\Users\aaaec\OneDrive\Desktop\lisans\uploads"
img_path = os.path.join(upload_dir, "032af755-6d01-4f6e-8724-2942486562b4.png") # 323768 bytes file

img = cv2.imread(img_path)
results = zxingcpp.read_barcodes(img)
if results:
    for result in results:
        print(f"ZXING FOUND: {result.text}")
else:
    print("ZXING failed on raw")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = zxingcpp.read_barcodes(gray)
    if res:
        print(f"ZXING GRAY FOUND: {res[0].text}")
    else:
        print("ZXING gray failed")
