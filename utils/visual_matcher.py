import cv2
import numpy as np
import os
import glob

class VisualMatcher:
    def __init__(self, reference_dir="assets/training_images", threshold=15):
        """
        Görsel kıyaslama motorunu başlatır.
        Referans görselleri belleğe alıp SIFT özelliklerini önceden hesaplar.
        
        :param threshold: Lowe's Ratio Test sonrası gereken minimum "iyi eşleşme" sayısı
        """
        self.reference_dir = reference_dir
        self.threshold = threshold 
        
        # SIFT motorunu başlat
        self.sift = cv2.SIFT_create()
        
        # FLANN tabanlı eşleştirici parametreleri (SIFT için kd-tree kullanılır)
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)
        
        # Önceden hesaplanmış referans verilerini tutacak sözlük
        self.reference_data = {}
        self._load_and_compute_references()

    def _load_and_compute_references(self):
        """
        Klasördeki tüm referans görsellerini tarar, SIFT özelliklerini çıkarır ve bellekte tutar.
        """
        # İspanya bölgeleri için tarama
        spain_path = os.path.join(self.reference_dir, "ispanya", "*.jpg") # png vb. desteklemek için güncellenebilir
        
        for file_path in glob.glob(spain_path):
            # Dosya adından bölge ismini çıkar (Örn: "catalunya.jpg" -> "catalunya")
            region_name = os.path.basename(file_path).split('.')[0] 
            
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"Uyarı: Referans görsel okunamadı -> {file_path}")
                continue
                
            # Keypoint (anahtar noktalar) ve Descriptor (tanımlayıcılar) hesapla
            kp, des = self.sift.detectAndCompute(img, None)
            
            self.reference_data[region_name] = {
                "keypoints": kp,
                "descriptors": des
            }
        print(f"VisualMatcher: {len(self.reference_data)} adet referans görsel başarıyla belleğe yüklendi.")

    def match_image(self, image_bytes: bytes) -> dict:
        """
        Yüklenen görseli referanslarla kıyaslar ve en iyi eşleşmeyi döndürür.
        """
        # 1. Byte verisini OpenCV formatına çevir ve gri tonlamaya al
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError("Görsel OpenCV tarafından okunamadı.")

        # 2. Yüklenen görselin SIFT özelliklerini çıkar
        kp_query, des_query = self.sift.detectAndCompute(img, None)
        
        if des_query is None or len(des_query) < 2:
            return {"match_found": False, "region": None, "score": 0, "message": "Görselde yeterli detay bulunamadı."}

        best_match = None
        highest_good_matches = 0

        # 3. Yüklenen görseli tüm referanslarla tek tek kıyasla
        for region_name, ref_data in self.reference_data.items():
            des_ref = ref_data["descriptors"]
            
            if des_ref is None or len(des_ref) < 2:
                continue
                
            # KNN (K-Nearest Neighbors) ile k=2 (en iyi 2 eşleşme) bularak Lowe's Ratio testine hazırlık
            try:
                matches = self.flann.knnMatch(des_query, des_ref, k=2)
            except Exception as e:
                continue

            good_matches = []
            # Lowe's Ratio Test: Sahte/zayıf eşleşmeleri filtreleme
            for match_set in matches:
                if len(match_set) == 2:
                    m, n = match_set
                    # Eğer birinci eşleşme, ikinci eşleşmeden %70 veya daha yakınsa bu "güçlü" bir eşleşmedir
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)

            num_good_matches = len(good_matches)
            
            if num_good_matches > highest_good_matches:
                highest_good_matches = num_good_matches
                best_match = region_name

        # 4. Sonuçları değerlendir (Threshold kontrolü ve Fallback)
        if highest_good_matches >= self.threshold:
            # İhtiyaca göre kalibre edilebilecek temel bir güven skoru hesabı
            confidence_score = min(100, int((highest_good_matches / (self.threshold * 2.5)) * 100))
            return {
                "match_found": True,
                "region": best_match,
                "score": confidence_score,
                "matches_count": highest_good_matches,
                "message": f"Bölge başarıyla tespit edildi."
            }
        else:
            return {
                "match_found": False,
                "region": None,
                "score": 0,
                "matches_count": highest_good_matches,
                "message": "Kart net okunamadı veya referanslarla eşleşmedi. Lütfen bölgeyi listeden seçin."
            }
