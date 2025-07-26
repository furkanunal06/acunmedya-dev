
import face_recognition
import cv2
import numpy as np
import os

class FaceRecognitionModel:
    def __init__(self):
        # face_recognition kütüphanesi modelleri otomatik olarak yönetir
        pass

    def get_face_embedding(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Resim yüklenemedi: {image_path}")
        
        # Görüntüdeki tüm yüzleri bul ve yüz embeddinglerini al
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)
        
        if len(face_encodings) == 0:
            return None, None # Yüz bulunamadı
        elif len(face_encodings) > 1:
            print("Uyarı: Resimde birden fazla yüz algılandı. Sadece ilk yüz işlenecektir.")

        # İlk algılanan yüzün embeddingini ve konumunu döndür
        # face_locations formatı: (top, right, bottom, left)
        # bbox formatı: [left, top, right, bottom]
        top, right, bottom, left = face_locations[0]
        bbox = [left, top, right, bottom]
        return face_encodings[0], bbox

    def compare_faces(self, embedding1, embedding2, tolerance=0.6):
        # Yüzleri karşılaştır ve benzerlik oranını döndür
        # face_distance, ne kadar farklı olduklarını gösterir (0=aynı, 1=tamamen farklı)
        # tolerance, eşik değeridir. Varsayılan 0.6, daha küçük değerler daha katı eşleşme demektir.
        face_distances = face_recognition.face_distance([embedding1], embedding2)
        similarity = 1 - face_distances[0] # Benzerlik oranı 0-1 arasında
        is_match = similarity > tolerance
        return similarity, is_match

    def detect_faces_in_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Resim yüklenemedi: {image_path}")
        
        face_locations = face_recognition.face_locations(img)
        
        detected_faces_info = []
        for face_location in face_locations:
            top, right, bottom, left = face_location
            bbox = [left, top, right, bottom]
            detected_faces_info.append({"bbox": bbox})
        return detected_faces_info

if __name__ == '__main__':
    # Test amaçlı kullanım
    face_model = FaceRecognitionModel()

    # Örnek bir resim kullan
    test_image_path = "./test_image.jpg"
    
    try:
        # Yüz embedding'i al
        embedding, bbox = face_model.get_face_embedding(test_image_path)

        if embedding is not None:
            print("Yüz embedding'i başarıyla alındı. Boyut:", embedding.shape)
            print("Bounding Box:", bbox)
            
            # İki embedding'i karşılaştır (aynı embedding'i kullanarak test)
            sim, is_match = face_model.compare_faces(embedding, embedding)
            print(f"Benzerlik: {sim:.4f}, Eşleşme: {is_match}")
        else:
            print("Resimde yüz bulunamadı.")

        # Resimdeki yüzleri algıla
        detected_faces = face_model.detect_faces_in_image(test_image_path)
        print(f"Algılanan yüz sayısı: {len(detected_faces)}")
        if detected_faces:
            print("İlk algılanan yüz bilgisi:", detected_faces[0])

    except Exception as e:
        print(f"Hata oluştu: {e}")



