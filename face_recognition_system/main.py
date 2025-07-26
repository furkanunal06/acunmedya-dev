import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.face_recognition import db, SystemSetting, User
from src.routes.face_recognition import face_bp
from src.routes.admin import admin_bp
from src.routes.auth import auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'face_recognition_secret_key_2024_jwt_secure'

# CORS ayarları - tüm origin'lere izin ver
CORS(app, origins="*")

# Blueprint'leri kaydet
app.register_blueprint(face_bp, url_prefix='/api/face')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Veritabanı ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Veritabanını başlat ve varsayılan ayarları ekle
with app.app_context():
    db.create_all()
    
    # Varsayılan admin kullanıcısı oluştur
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@facerecognition.com',
            full_name='Sistem Yöneticisi',
            is_admin=True,
            is_active=True
        )
        db.session.add(admin_user)
        print("Varsayılan admin kullanıcısı oluşturuldu: admin / admin123")
    
    # Varsayılan sistem ayarlarını ekle
    default_settings = [
        {'key': 'face_threshold', 'value': '0.6', 'description': 'Yüz tanıma eşik değeri (0.0-1.0)'},
        {'key': 'max_face_enrollments', 'value': '10', 'description': 'Kullanıcı başına maksimum yüz kaydı sayısı'},
        {'key': 'min_face_enrollments', 'value': '5', 'description': 'Kullanıcı başına minimum yüz kaydı sayısı'},
        {'key': 'log_retention_days', 'value': '90', 'description': 'Log kayıtlarının saklanma süresi (gün)'},
        {'key': 'allow_multiple_faces', 'value': 'false', 'description': 'Aynı anda birden fazla yüz algılamaya izin ver'},
        {'key': 'jwt_expiry_hours', 'value': '24', 'description': 'JWT token geçerlilik süresi (saat)'},
        {'key': 'max_login_attempts', 'value': '5', 'description': 'Maksimum başarısız giriş denemesi'},
        {'key': 'account_lockout_minutes', 'value': '30', 'description': 'Hesap kilitleme süresi (dakika)'}
    ]
    
    for setting_data in default_settings:
        existing_setting = SystemSetting.query.filter_by(setting_key=setting_data['key']).first()
        if not existing_setting:
            setting = SystemSetting(
                setting_key=setting_data['key'],
                setting_value=setting_data['value'],
                description=setting_data['description']
            )
            db.session.add(setting)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return {
                'message': 'Face Recognition API is running',
                'version': '1.0.0',
                'endpoints': {
                    'face': '/api/face/*',
                    'admin': '/api/admin/*',
                    'auth': '/api/auth/*',
                    'health': '/health'
                },
                'auth_info': {
                    'default_admin': 'admin',
                    'default_password': 'admin123',
                    'note': 'Change default password after first login'
                }
            }, 200

@app.route('/health', methods=['GET'])
def health_check():
    """Sistem durumu kontrolü"""
    try:
        # Veritabanı bağlantısını test et
        user_count = User.query.count()
        
        return {
            'status': 'healthy',
            'message': 'Face Recognition API is running',
            'version': '1.0.0',
            'database': 'connected',
            'users_count': user_count,
            'features': [
                'Face Enrollment',
                'Face Authentication', 
                'Admin Panel',
                'JWT Security',
                'Access Logging'
            ]
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e)
        }, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

