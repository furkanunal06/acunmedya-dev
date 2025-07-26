
import cv2
import face_recognition
import os

image_path = "./test_image.jpg"

if not os.path.exists(image_path):
    print(f"Hata: Resim dosyası bulunamadı: {image_path}")
else:
    # OpenCV ile resmi oku
    img_cv2 = cv2.imread(image_path)
    if img_cv2 is None:
        print(f"Hata: OpenCV resmi okuyamadı: {image_path}")
    else:
        print(f"OpenCV ile okunan resim boyutu: {img_cv2.shape}")
        # Gri tonlamalıya çevirip kaydet (görsel kontrol için)
        cv2.imwrite("./test_image_gray.jpg", cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY))
        print("Gri tonlamalı resim test_image_gray.jpg olarak kaydedildi.")

        # face_recognition kütüphanesi ile resmi oku
        try:
            img_face_rec = face_recognition.load_image_file(image_path)
            print(f"face_recognition ile okunan resim boyutu: {img_face_rec.shape}")
            
            # Yüz algılama testi
            face_locations = face_recognition.face_locations(img_face_rec)
            if len(face_locations) > 0:
                print(f"face_recognition ile {len(face_locations)} yüz algılandı.")
                for i, face_location in enumerate(face_locations):
                    top, right, bottom, left = face_location
                    print(f"Yüz {i+1} konumu: Top: {top}, Right: {right}, Bottom: {bottom}, Left: {left}")
            else:
                print("face_recognition ile yüz algılanamadı.")

        except Exception as e:
            print(f"face_recognition ile resim yüklenirken veya işlenirken hata oluştu: {e}")



