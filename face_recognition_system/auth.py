from flask import Blueprint, request, jsonify, current_app
from src.models.face_recognition import db, User
import jwt
from datetime import datetime, timedelta
from functools import wraps
import hashlib

auth_bp = Blueprint('auth', __name__)

def generate_password_hash(password):
    """Basit password hash fonksiyonu"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(password_hash, password):
    """Password hash kontrolü"""
    return password_hash == hashlib.sha256(password.encode()).hexdigest()

def token_required(f):
    """JWT token gerekli decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Header'dan token al
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer TOKEN" formatından token'ı al
            except IndexError:
                return jsonify({'error': 'Token formatı hatalı'}), 401
        
        if not token:
            return jsonify({'error': 'Token eksik'}), 401
        
        try:
            # Token'ı decode et
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'Geçersiz kullanıcı'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token süresi dolmuş'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Geçersiz token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Admin yetkisi gerekli decorator"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin yetkisi gerekli'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """Admin girişi"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Kullanıcı adı ve şifre gerekli'}), 400
        
        username = data['username']
        password = data['password']
        
        # Kullanıcıyı bul
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.is_active:
            return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401
        
        # Basit şifre kontrolü (gerçek uygulamada hash'lenmiş şifre kullanılmalı)
        # Şimdilik admin kullanıcıları için basit bir şifre sistemi
        if user.is_admin and password == "admin123":  # Varsayılan admin şifresi
            # JWT token oluştur
            token_payload = {
                'user_id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
                'exp': datetime.utcnow() + timedelta(hours=24)  # 24 saat geçerli
            }
            
            token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'token': token,
                'user': user.to_dict(),
                'expires_in': 24 * 60 * 60  # saniye cinsinden
            }), 200
        else:
            return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Token yenileme"""
    try:
        # Yeni token oluştur
        token_payload = {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        new_token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': new_token,
            'expires_in': 24 * 60 * 60
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Çıkış (token'ı geçersiz kılma - client tarafında silinmeli)"""
    return jsonify({'message': 'Başarıyla çıkış yapıldı'}), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Mevcut kullanıcı bilgilerini getir"""
    return jsonify({'user': current_user.to_dict()}), 200

@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    """Şifre değiştirme"""
    try:
        data = request.get_json()
        
        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Eski ve yeni şifre gerekli'}), 400
        
        old_password = data['old_password']
        new_password = data['new_password']
        
        # Eski şifre kontrolü (basit implementasyon)
        if old_password != "admin123":  # Varsayılan şifre
            return jsonify({'error': 'Eski şifre hatalı'}), 400
        
        # Yeni şifre uzunluk kontrolü
        if len(new_password) < 6:
            return jsonify({'error': 'Yeni şifre en az 6 karakter olmalı'}), 400
        
        # Şifre değiştirme işlemi (gerçek uygulamada hash'lenmiş şifre kullanılmalı)
        # Bu basit implementasyonda şifre değiştirme simüle edilir
        
        return jsonify({'message': 'Şifre başarıyla değiştirildi'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

# Korumalı endpoint örnekleri
@auth_bp.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    """Korumalı endpoint örneği"""
    return jsonify({
        'message': 'Bu korumalı bir endpoint',
        'user': current_user.username
    }), 200

@auth_bp.route('/admin-only', methods=['GET'])
@token_required
@admin_required
def admin_only_route(current_user):
    """Sadece admin'ler için endpoint örneği"""
    return jsonify({
        'message': 'Bu sadece admin\'ler için',
        'admin': current_user.username
    }), 200

