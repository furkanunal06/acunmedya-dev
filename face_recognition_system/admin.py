
from flask import Blueprint, request, jsonify
from src.models.face_recognition import db, User, AccessLog, SystemSetting
from datetime import datetime, timedelta
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/logs', methods=['GET'])
def get_access_logs():
    """Giriş loglarını getir"""
    try:
        # Query parametreleri
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        success_filter = request.args.get('success', None)
        user_id = request.args.get('user_id', None, type=int)
        days = request.args.get('days', 30, type=int)
        
        # Tarih filtresi
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query oluştur
        query = AccessLog.query.filter(AccessLog.timestamp >= start_date)
        
        if success_filter is not None:
            success_bool = success_filter.lower() == 'true'
            query = query.filter(AccessLog.success == success_bool)
        
        if user_id:
            query = query.filter(AccessLog.user_id == user_id)
        
        # Sıralama ve sayfalama
        query = query.order_by(desc(AccessLog.timestamp))
        logs = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """Sistem istatistiklerini getir"""
    try:
        # Son 30 günün istatistikleri
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Toplam kullanıcı sayısı
        total_users = User.query.count()
        active_users = User.query.filter(User.is_active == True).count()
        
        # Giriş istatistikleri
        total_attempts = AccessLog.query.filter(AccessLog.timestamp >= thirty_days_ago).count()
        successful_attempts = AccessLog.query.filter(
            AccessLog.timestamp >= thirty_days_ago,
            AccessLog.success == True
        ).count()
        failed_attempts = total_attempts - successful_attempts
        
        # Başarı oranı
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Günlük giriş sayıları (son 7 gün)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(AccessLog.timestamp).label('date'),
            func.count(AccessLog.id).label('total'),
            func.sum(func.cast(AccessLog.success, db.Integer)).label('successful')
        ).filter(
            AccessLog.timestamp >= seven_days_ago
        ).group_by(
            func.date(AccessLog.timestamp)
        ).order_by(
            func.date(AccessLog.timestamp)
        ).all()
        
        daily_data = []
        for stat in daily_stats:
            daily_data.append({
                'date': str(stat.date),  # isoformat yerine str kullan
                'total_attempts': stat.total,
                'successful_attempts': stat.successful or 0,
                'failed_attempts': stat.total - (stat.successful or 0)
            })
        
        # En aktif kullanıcılar
        top_users = db.session.query(
            User.username,
            User.full_name,
            func.count(AccessLog.id).label('login_count')
        ).join(
            AccessLog, User.id == AccessLog.user_id
        ).filter(
            AccessLog.timestamp >= thirty_days_ago,
            AccessLog.success == True
        ).group_by(
            User.id, User.username, User.full_name
        ).order_by(
            desc(func.count(AccessLog.id))
        ).limit(10).all()
        
        top_users_data = []
        for user in top_users:
            top_users_data.append({
                'username': user.username,
                'full_name': user.full_name,
                'login_count': user.login_count
            })
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'total_attempts_30d': total_attempts,
            'successful_attempts_30d': successful_attempts,
            'failed_attempts_30d': failed_attempts,
            'success_rate_30d': round(success_rate, 2),
            'daily_stats_7d': daily_data,
            'top_users_30d': top_users_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Sistem ayarlarını getir"""
    try:
        settings = SystemSetting.query.all()
        return jsonify([setting.to_dict() for setting in settings]), 200
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@admin_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Sistem ayarlarını güncelle"""
    try:
        data = request.get_json()
        
        if 'settings' not in data:
            return jsonify({'error': 'Ayarlar verisi gerekli'}), 400
        
        updated_count = 0
        for setting_data in data['settings']:
            if 'key' not in setting_data or 'value' not in setting_data:
                continue
            
            setting = SystemSetting.query.filter_by(setting_key=setting_data['key']).first()
            
            if setting:
                setting.setting_value = str(setting_data['value'])
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSetting(
                    setting_key=setting_data['key'],
                    setting_value=str(setting_data['value']),
                    description=setting_data.get('description', '')
                )
                db.session.add(setting)
            
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{updated_count} ayar güncellendi',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
def toggle_user_status(user_id):
    """Kullanıcı durumunu aktif/pasif yap"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status = 'aktif' if user.is_active else 'pasif'
        return jsonify({
            'message': f'Kullanıcı {status} duruma getirildi',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/make-admin', methods=['PUT'])
def make_user_admin(user_id):
    """Kullanıcıyı admin yap"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        user.is_admin = True
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Kullanıcı admin yetkisi aldı',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@admin_bp.route('/cleanup-logs', methods=['DELETE'])
def cleanup_old_logs():
    """Eski logları temizle"""
    try:
        days = request.args.get('days', 90, type=int)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = db.session.query(AccessLog).filter(AccessLog.timestamp < cutoff_date).delete()
        db.session.commit()
        
        return jsonify({
            'message': f'{deleted_count} eski log kaydı silindi',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

