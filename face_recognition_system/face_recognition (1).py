from flask import Blueprint, request, jsonify, current_app
from src.models.face_recognition import db, User, FaceEmbedding, AccessLog, SystemSetting
import face_recognition
import cv2
import numpy as np
import os
import tempfile
import base64
from datetime import datetime
import io
from PIL import Image

face_bp = Blueprint('face', __name__)

class FaceRecognitionService:
    def __init__(self):
        pass

    def get_face_embedding(self, image_data):
        """Base64 encoded image'den yüz embedding'i çıkar"""
        try:
            # Base64'ü decode et
            image_bytes = base64.b64decode(image_data)
            
            # PIL Image'e çevir
            image = Image.open(io.BytesIO(image_bytes))
            
            # NumPy array'e çevir
            img_array = np.array(image)
            
            # RGB formatına çevir (face_recognition RGB bekler)
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            else:
                img_rgb = img_array
            
            # Yüz algılama ve embedding çıkarma
            face_locations = face_recognition.face_locations(img_rgb)
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            
            if len(face_encodings) == 0:
                return None, None, "Resimde yüz bulunamadı"
            elif len(face_encodings) > 1:
                return None, None, "Resimde birden fazla yüz algılandı"
            
            # İlk yüzün embedding'ini ve konumunu döndür
            top, right, bottom, left = face_locations[0]
            bbox = [left, top, right, bottom]
            
            return face_encodings[0], bbox, None
            
        except Exception as e:
            return None, None, f"Resim işleme hatası: {str(e)}"

    def compare_faces(self, embedding1, embedding2, tolerance=0.6):
        """İki yüz embedding'ini karşılaştır"""
        face_distances = face_recognition.face_distance([embedding1], embedding2)
        similarity = 1 - face_distances[0]
        is_match = similarity > tolerance
        return similarity, is_match

face_service = FaceRecognitionService()

@face_bp.route('/enroll', methods=['POST'])
def enroll_face():
    """Yeni kullanıcı yüz verisi kaydetme"""
    try:
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['username', 'email', 'full_name', 'images']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Eksik alan: {field}'}), 400
        
        # Kullanıcının zaten var olup olmadığını kontrol et
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Kullanıcı adı veya email zaten mevcut'}), 400
        
        # Yeni kullanıcı oluştur
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            is_admin=data.get('is_admin', False)
        )
        
        db.session.add(user)
        db.session.flush()  # ID'yi al
        
        # Yüz verilerini işle
        embeddings_added = 0
        for i, image_data in enumerate(data['images']):
            embedding, bbox, error = face_service.get_face_embedding(image_data['data'])
            
            if error:
                # Hata durumunda kullanıcıyı sil
                db.session.rollback()
                return jsonify({'error': f'Resim {i+1}: {error}'}), 400
            
            # Embedding'i kaydet
            face_embedding = FaceEmbedding(
                user_id=user.id,
                pose_type=image_data.get('pose_type', f'pose_{i+1}'),
                quality_score=image_data.get('quality_score', 0.8)
            )
            face_embedding.set_embedding_vector(embedding)
            
            db.session.add(face_embedding)
            embeddings_added += 1
        
        # Minimum embedding sayısını kontrol et
        if embeddings_added < 5:
            db.session.rollback()
            return jsonify({'error': 'En az 5 farklı poz gereklidir'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Kullanıcı başarıyla kaydedildi',
            'user_id': user.id,
            'embeddings_count': embeddings_added
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@face_bp.route('/authenticate', methods=['POST'])
def authenticate_face():
    """Yüz ile kimlik doğrulama"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Resim verisi gerekli'}), 400
        
        # IP adresini al
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        
        # Gelen resimden embedding çıkar
        embedding, bbox, error = face_service.get_face_embedding(data['image'])
        
        if error:
            # Başarısız girişi logla
            log = AccessLog(
                ip_address=ip_address,
                success=False,
                error_message=error
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'error': error}), 400
        
        # Eşik değerini al
        threshold_setting = SystemSetting.query.filter_by(setting_key='face_threshold').first()
        threshold = float(threshold_setting.setting_value) if threshold_setting else 0.6
        
        # Tüm kayıtlı embedding'lerle karşılaştır
        best_match = None
        best_similarity = 0
        
        all_embeddings = FaceEmbedding.query.join(User).filter(User.is_active == True).all()
        
        for face_embedding in all_embeddings:
            stored_embedding = face_embedding.get_embedding_vector()
            similarity, is_match = face_service.compare_faces(stored_embedding, embedding, threshold)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = face_embedding
        
        # Sonucu değerlendir
        if best_match and best_similarity > threshold:
            # Başarılı giriş
            user = best_match.user
            log = AccessLog(
                user_id=user.id,
                ip_address=ip_address,
                success=True,
                similarity_score=best_similarity
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'similarity': best_similarity,
                'message': 'Kimlik doğrulama başarılı'
            }), 200
        else:
            # Başarısız giriş
            log = AccessLog(
                ip_address=ip_address,
                success=False,
                similarity_score=best_similarity,
                error_message=f'Eşik değeri altında benzerlik: {best_similarity:.4f}'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'similarity': best_similarity,
                'message': 'Kimlik doğrulama başarısız'
            }), 401
            
    except Exception as e:
        # Hata durumunda logla
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        log = AccessLog(
            ip_address=ip_address,
            success=False,
            error_message=f'Sunucu hatası: {str(e)}'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@face_bp.route('/users', methods=['GET'])
def get_users():
    """Kayıtlı kullanıcıları listele"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@face_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Kullanıcıyı ve yüz verilerini sil"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Kullanıcı başarıyla silindi'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@face_bp.route('/detect', methods=['POST'])
def detect_faces():
    """Resimde yüz algılama"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Resim verisi gerekli'}), 400
        
        embedding, bbox, error = face_service.get_face_embedding(data['image'])
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'faces_detected': 1,
            'bbox': bbox,
            'message': 'Yüz başarıyla algılandı'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

