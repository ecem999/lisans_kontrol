import os
import cv2
from pyzbar.pyzbar import decode

upload_dir = r"C:\Users\aaaec\OneDrive\Desktop\lisans\uploads"
img_path = os.path.join(upload_dir, "e3875158-6da8-4f2f-9f53-173b380064cc.png")

img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
inverted = cv2.bitwise_not(gray)

objs = decode(inverted)
if objs:
    print(f"FOUND INVERTED: {objs[0].data.decode('utf-8')}")
else:
    print("Inverted failed")

# Try to find the exact file that is 323768 bytes
for file in os.listdir(upload_dir):
    p = os.path.join(upload_dir, file)
    if os.path.getsize(p) == 323768:
        print(f"Testing 323768 byte file: {file}")
        img2 = cv2.imread(p)
        g = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(g)
        o = decode(inv)
        if o:
            print(f"FOUND INVERTED 323768: {o[0].data.decode('utf-8')}")
        break
