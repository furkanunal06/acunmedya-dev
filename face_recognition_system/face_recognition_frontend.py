import streamlit as st
import requests
import base64
import cv2
import numpy as np
from PIL import Image
import io
import json
from datetime import datetime

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Yüz Tanıma Sistemi",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:5000/api"

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .success-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 10px 0;
    }
    .error-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 10px 0;
    }
    .info-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def image_to_base64(image):
    """PIL Image'i base64 string'e çevir"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def display_message(message, message_type="info"):
    """Mesaj gösterme fonksiyonu"""
    if message_type == "success":
        st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
    elif message_type == "error":
        st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="info-box">{message}</div>', unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🔐 Yüz Tanıma Sistemi</h1>', unsafe_allow_html=True)
    
    # Sidebar menü
    st.sidebar.title("📋 Menü")
    page = st.sidebar.selectbox(
        "Sayfa Seçin",
        ["🏠 Ana Sayfa", "👤 Yüz Kaydı", "🔍 Yüz Doğrulama", "📊 Admin Panel", "⚙️ Sistem Durumu"]
    )
    
    if page == "🏠 Ana Sayfa":
        show_home_page()
    elif page == "👤 Yüz Kaydı":
        show_enrollment_page()
    elif page == "🔍 Yüz Doğrulama":
        show_authentication_page()
    elif page == "📊 Admin Panel":
        show_admin_panel()
    elif page == "⚙️ Sistem Durumu":
        show_system_status()

def show_home_page():
    st.header("Hoş Geldiniz!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Yüz Kaydı")
        st.write("Yeni kullanıcılar için yüz verilerini sisteme kaydedin.")
        st.write("• Minimum 5 farklı poz gereklidir")
        st.write("• Yüksek kaliteli resimler kullanın")
        st.write("• İyi ışıklandırma önemlidir")
    
    with col2:
        st.subheader("🔍 Yüz Doğrulama")
        st.write("Kayıtlı kullanıcılar için kimlik doğrulama yapın.")
        st.write("• Kamera ile canlı doğrulama")
        st.write("• Yüksek güvenlik seviyesi")
        st.write("• Hızlı sonuç alma")
    
    with col3:
        st.subheader("📊 Admin Panel")
        st.write("Sistem yönetimi ve istatistikler.")
        st.write("• Kullanıcı yönetimi")
        st.write("• Giriş logları")
        st.write("• Sistem ayarları")

def show_enrollment_page():
    st.header("👤 Yeni Kullanıcı Kaydı")
    
    with st.form("enrollment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Kullanıcı Bilgileri")
            username = st.text_input("Kullanıcı Adı", placeholder="kullanici_adi")
            email = st.text_input("E-posta", placeholder="ornek@email.com")
            full_name = st.text_input("Ad Soyad", placeholder="Ad Soyad")
            is_admin = st.checkbox("Admin Yetkisi Ver")
        
        with col2:
            st.subheader("Yüz Resimleri")
            st.write("Lütfen en az 5 farklı pozda resim yükleyin:")
            
            uploaded_files = st.file_uploader(
                "Resim Dosyalarını Seçin",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                help="Farklı açılardan, farklı ifadelerle çekilmiş resimler yükleyin"
            )
        
        submitted = st.form_submit_button("Kullanıcıyı Kaydet", type="primary")
        
        if submitted:
            if not username or not email or not full_name:
                display_message("Lütfen tüm kullanıcı bilgilerini doldurun!", "error")
                return
            
            if not uploaded_files or len(uploaded_files) < 5:
                display_message("En az 5 resim yüklemeniz gerekiyor!", "error")
                return
            
            # Resimleri işle
            images_data = []
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    image = Image.open(uploaded_file)
                    # Resmi RGB formatına çevir
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Base64'e çevir
                    img_base64 = image_to_base64(image)
                    
                    images_data.append({
                        "data": img_base64,
                        "pose_type": f"pose_{i+1}",
                        "quality_score": 0.8
                    })
                except Exception as e:
                    display_message(f"Resim {i+1} işlenirken hata: {str(e)}", "error")
                    return
            
            # API'ye gönder
            try:
                payload = {
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "is_admin": is_admin,
                    "images": images_data
                }
                
                response = requests.post(f"{API_BASE_URL}/face/enroll", json=payload)
                
                if response.status_code == 201:
                    result = response.json()
                    display_message(
                        f"✅ Kullanıcı başarıyla kaydedildi! "
                        f"Kullanıcı ID: {result['user_id']}, "
                        f"Kayıtlı yüz sayısı: {result['embeddings_count']}", 
                        "success"
                    )
                else:
                    error_msg = response.json().get('error', 'Bilinmeyen hata')
                    display_message(f"❌ Kayıt başarısız: {error_msg}", "error")
                    
            except requests.exceptions.ConnectionError:
                display_message("❌ API sunucusuna bağlanılamıyor. Sunucunun çalıştığından emin olun.", "error")
            except Exception as e:
                display_message(f"❌ Beklenmeyen hata: {str(e)}", "error")

def show_authentication_page():
    st.header("🔍 Yüz Doğrulama")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Resim Yükleme")
        
        # Kamera veya dosya seçimi
        input_method = st.radio(
            "Resim kaynağını seçin:",
            ["📷 Kamera", "📁 Dosya Yükleme"]
        )
        
        image = None
        
        if input_method == "📷 Kamera":
            camera_image = st.camera_input("Fotoğraf çekin")
            if camera_image:
                image = Image.open(camera_image)
        else:
            uploaded_file = st.file_uploader(
                "Resim dosyası seçin",
                type=['jpg', 'jpeg', 'png']
            )
            if uploaded_file:
                image = Image.open(uploaded_file)
        
        if image:
            st.image(image, caption="Yüklenen Resim", use_column_width=True)
            
            if st.button("🔍 Kimlik Doğrulama Yap", type="primary"):
                try:
                    # Resmi RGB formatına çevir
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Base64'e çevir
                    img_base64 = image_to_base64(image)
                    
                    # API'ye gönder
                    payload = {"image": img_base64}
                    response = requests.post(f"{API_BASE_URL}/face/authenticate", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result['success']:
                            user = result['user']
                            similarity = result['similarity']
                            
                            with col2:
                                st.subheader("✅ Doğrulama Başarılı")
                                st.success(f"Hoş geldiniz, {user['full_name']}!")
                                st.write(f"**Kullanıcı Adı:** {user['username']}")
                                st.write(f"**E-posta:** {user['email']}")
                                st.write(f"**Benzerlik Oranı:** %{similarity*100:.2f}")
                                st.write(f"**Giriş Zamanı:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            with col2:
                                st.subheader("❌ Doğrulama Başarısız")
                                st.error("Kimlik doğrulanamadı!")
                                st.write(f"**Benzerlik Oranı:** %{result['similarity']*100:.2f}")
                                st.write("Lütfen tekrar deneyin veya kayıtlı bir kullanıcı olduğunuzdan emin olun.")
                    else:
                        error_msg = response.json().get('error', 'Bilinmeyen hata')
                        display_message(f"❌ Doğrulama hatası: {error_msg}", "error")
                        
                except requests.exceptions.ConnectionError:
                    display_message("❌ API sunucusuna bağlanılamıyor.", "error")
                except Exception as e:
                    display_message(f"❌ Beklenmeyen hata: {str(e)}", "error")

def show_admin_panel():
    st.header("📊 Admin Panel")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Kullanıcılar", "📋 Loglar", "📈 İstatistikler", "⚙️ Ayarlar"])
    
    with tab1:
        st.subheader("Kayıtlı Kullanıcılar")
        
        try:
            response = requests.get(f"{API_BASE_URL}/face/users")
            if response.status_code == 200:
                users = response.json()
                
                if users:
                    for user in users:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            status_icon = "🟢" if user['is_active'] else "🔴"
                            admin_icon = "👑" if user['is_admin'] else "👤"
                            st.write(f"{status_icon} {admin_icon} **{user['full_name']}** ({user['username']})")
                            st.write(f"📧 {user['email']}")
                        
                        with col2:
                            if st.button(f"🗑️ Sil", key=f"delete_{user['id']}"):
                                delete_response = requests.delete(f"{API_BASE_URL}/face/users/{user['id']}")
                                if delete_response.status_code == 200:
                                    st.success("Kullanıcı silindi!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Silme işlemi başarısız!")
                        
                        with col3:
                            if st.button(f"⚙️ Düzenle", key=f"edit_{user['id']}"):
                                st.info("Düzenleme özelliği yakında eklenecek!")
                        
                        st.divider()
                else:
                    st.info("Henüz kayıtlı kullanıcı bulunmuyor.")
            else:
                st.error("Kullanıcı listesi alınamadı.")
        except:
            st.error("API sunucusuna bağlanılamıyor.")
    
    with tab2:
        st.subheader("Giriş Logları")
        
        try:
            response = requests.get(f"{API_BASE_URL}/admin/logs")
            if response.status_code == 200:
                logs_data = response.json()
                logs = logs_data['logs']
                
                if logs:
                    for log in logs[:20]:  # Son 20 log
                        status_icon = "✅" if log['success'] else "❌"
                        timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                        
                        st.write(f"{status_icon} **{timestamp.strftime('%Y-%m-%d %H:%M:%S')}** - IP: {log['ip_address']}")
                        
                        if log['success'] and log['similarity_score']:
                            st.write(f"   Benzerlik: %{log['similarity_score']*100:.2f}")
                        elif log['error_message']:
                            st.write(f"   Hata: {log['error_message']}")
                        
                        st.divider()
                else:
                    st.info("Henüz log kaydı bulunmuyor.")
            else:
                st.error("Log verileri alınamadı.")
        except:
            st.error("API sunucusuna bağlanılamıyor.")
    
    with tab3:
        st.subheader("Sistem İstatistikleri")
        
        try:
            response = requests.get(f"{API_BASE_URL}/admin/stats")
            if response.status_code == 200:
                stats = response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Toplam Kullanıcı", stats['total_users'])
                
                with col2:
                    st.metric("Aktif Kullanıcı", stats['active_users'])
                
                with col3:
                    st.metric("Başarılı Giriş (30g)", stats['successful_attempts_30d'])
                
                with col4:
                    st.metric("Başarı Oranı", f"%{stats['success_rate_30d']}")
                
                # Günlük istatistikler
                if stats['daily_stats_7d']:
                    st.subheader("Son 7 Günün Giriş İstatistikleri")
                    daily_data = stats['daily_stats_7d']
                    
                    dates = [item['date'] for item in daily_data]
                    successful = [item['successful_attempts'] for item in daily_data]
                    failed = [item['failed_attempts'] for item in daily_data]
                    
                    chart_data = {
                        'Tarih': dates,
                        'Başarılı': successful,
                        'Başarısız': failed
                    }
                    
                    st.line_chart(chart_data, x='Tarih')
            else:
                st.error("İstatistik verileri alınamadı.")
        except:
            st.error("API sunucusuna bağlanılamıyor.")
    
    with tab4:
        st.subheader("Sistem Ayarları")
        
        try:
            response = requests.get(f"{API_BASE_URL}/admin/settings")
            if response.status_code == 200:
                settings = response.json()
                
                with st.form("settings_form"):
                    updated_settings = []
                    
                    for setting in settings:
                        if setting['setting_key'] == 'face_threshold':
                            value = st.slider(
                                "Yüz Tanıma Eşik Değeri",
                                min_value=0.0,
                                max_value=1.0,
                                value=float(setting['setting_value']),
                                step=0.01,
                                help=setting['description']
                            )
                            updated_settings.append({
                                'key': setting['setting_key'],
                                'value': value,
                                'description': setting['description']
                            })
                        elif setting['setting_key'] in ['max_face_enrollments', 'min_face_enrollments', 'log_retention_days']:
                            value = st.number_input(
                                setting['description'],
                                min_value=1,
                                value=int(setting['setting_value']),
                                help=setting['description']
                            )
                            updated_settings.append({
                                'key': setting['setting_key'],
                                'value': value,
                                'description': setting['description']
                            })
                    
                    if st.form_submit_button("Ayarları Kaydet", type="primary"):
                        update_response = requests.put(
                            f"{API_BASE_URL}/admin/settings",
                            json={'settings': updated_settings}
                        )
                        
                        if update_response.status_code == 200:
                            st.success("Ayarlar başarıyla güncellendi!")
                        else:
                            st.error("Ayarlar güncellenemedi!")
            else:
                st.error("Ayar verileri alınamadı.")
        except:
            st.error("API sunucusuna bağlanılamıyor.")

def show_system_status():
    st.header("⚙️ Sistem Durumu")
    
    # API durumu kontrolü
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API Sunucusu: Çalışıyor")
            health_data = response.json()
            st.write(f"**Versiyon:** {health_data.get('version', 'Bilinmiyor')}")
            st.write(f"**Durum:** {health_data.get('status', 'Bilinmiyor')}")
        else:
            st.error("❌ API Sunucusu: Hata")
    except:
        st.error("❌ API Sunucusu: Bağlantı Kurulamıyor")
    
    st.divider()
    
    # Sistem bilgileri
    st.subheader("Sistem Bilgileri")
    st.write(f"**Frontend:** Streamlit {st.__version__}")
    st.write(f"**API Base URL:** {API_BASE_URL}")
    st.write(f"**Zaman:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

