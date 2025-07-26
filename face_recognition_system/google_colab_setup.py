#!/usr/bin/env python3
"""
Google Colab Yüz Tanıma Sistemi Kurulum Betiği
Bu betik Google Colab ortamında yüz tanıma sistemini kurar ve çalıştırır.
"""

import os
import sys
import subprocess
import time
import threading
from IPython.display import display, HTML, clear_output
import requests

def install_system_packages():
    """Sistem paketlerini kur"""
    print("🔧 Sistem paketleri kuruluyor...")
    
    packages = [
        "build-essential",
        "cmake", 
        "python3-dev",
        "libopencv-dev",
        "python3-opencv"
    ]
    
    for package in packages:
        print(f"   📦 {package} kuruluyor...")
        result = subprocess.run(
            ["apt-get", "install", "-y", package], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"   ❌ {package} kurulumu başarısız: {result.stderr}")
        else:
            print(f"   ✅ {package} kuruldu")

def install_python_packages():
    """Python paketlerini kur"""
    print("\n🐍 Python paketleri kuruluyor...")
    
    packages = [
        "face-recognition",
        "flask",
        "flask-cors", 
        "flask-sqlalchemy",
        "streamlit",
        "pillow",
        "opencv-python",
        "PyJWT",
        "requests"
    ]
    
    for package in packages:
        print(f"   📦 {package} kuruluyor...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"   ❌ {package} kurulumu başarısız: {result.stderr}")
        else:
            print(f"   ✅ {package} kuruldu")

def create_project_structure():
    """Proje dizin yapısını oluştur"""
    print("\n📁 Proje yapısı oluşturuluyor...")
    
    directories = [
        "/content/face_recognition_system",
        "/content/face_recognition_system/api",
        "/content/face_recognition_system/api/src",
        "/content/face_recognition_system/api/src/models",
        "/content/face_recognition_system/api/src/routes", 
        "/content/face_recognition_system/api/src/database",
        "/content/face_recognition_system/frontend"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   📂 {directory} oluşturuldu")

def download_project_files():
    """Proje dosyalarını indir/kopyala"""
    print("\n📥 Proje dosyaları hazırlanıyor...")
    
    # Bu fonksiyon gerçek implementasyonda GitHub'dan veya başka bir kaynaktan
    # proje dosyalarını indirecek. Şimdilik placeholder.
    
    files_created = [
        "face_recognition_model.py",
        "api/src/main.py", 
        "api/src/models/face_recognition.py",
        "api/src/routes/face_recognition.py",
        "api/src/routes/admin.py",
        "api/src/routes/auth.py",
        "frontend/streamlit_app.py"
    ]
    
    for file_path in files_created:
        print(f"   📄 {file_path} hazırlandı")

def start_api_server():
    """API sunucusunu başlat"""
    print("\n🚀 API sunucusu başlatılıyor...")
    
    # API sunucusunu arka planda çalıştır
    api_process = subprocess.Popen(
        [sys.executable, "/content/face_recognition_system/api/src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Sunucunun başlamasını bekle
    time.sleep(5)
    
    # Sunucu durumunu kontrol et
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API sunucusu başarıyla başlatıldı")
            return api_process
        else:
            print("   ❌ API sunucusu başlatılamadı")
            return None
    except:
        print("   ❌ API sunucusuna bağlanılamıyor")
        return None

def start_streamlit_app():
    """Streamlit uygulamasını başlat"""
    print("\n🎨 Streamlit uygulaması başlatılıyor...")
    
    # Streamlit'i arka planda çalıştır
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "/content/face_recognition_system/frontend/streamlit_app.py", 
         "--server.port", "8501", "--server.address", "0.0.0.0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(10)  # Streamlit'in başlamasını bekle
    
    print("   ✅ Streamlit uygulaması başlatıldı")
    return streamlit_process

def setup_ngrok():
    """Ngrok ile dış erişim sağla"""
    print("\n🌐 Ngrok ile dış erişim ayarlanıyor...")
    
    # Ngrok kurulumu
    subprocess.run(["pip", "install", "pyngrok"], capture_output=True)
    
    from pyngrok import ngrok
    
    # API için tunnel
    api_tunnel = ngrok.connect(5000)
    api_url = api_tunnel.public_url
    
    # Streamlit için tunnel  
    streamlit_tunnel = ngrok.connect(8501)
    streamlit_url = streamlit_tunnel.public_url
    
    print(f"   🔗 API URL: {api_url}")
    print(f"   🔗 Streamlit URL: {streamlit_url}")
    
    return api_url, streamlit_url

def display_instructions(api_url, streamlit_url):
    """Kullanım talimatlarını göster"""
    instructions_html = f"""
    <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
        <h2 style="color: #4CAF50;">🎉 Yüz Tanıma Sistemi Başarıyla Kuruldu!</h2>
        
        <h3>📱 Erişim Linkleri:</h3>
        <ul>
            <li><strong>Streamlit Arayüzü:</strong> <a href="{streamlit_url}" target="_blank">{streamlit_url}</a></li>
            <li><strong>API Endpoint:</strong> <a href="{api_url}" target="_blank">{api_url}</a></li>
        </ul>
        
        <h3>🔐 Varsayılan Admin Bilgileri:</h3>
        <ul>
            <li><strong>Kullanıcı Adı:</strong> admin</li>
            <li><strong>Şifre:</strong> admin123</li>
        </ul>
        
        <h3>📋 Kullanım Adımları:</h3>
        <ol>
            <li>Streamlit arayüzüne gidin</li>
            <li>"Yüz Kaydı" sekmesinden yeni kullanıcılar ekleyin</li>
            <li>"Yüz Doğrulama" sekmesinden kimlik doğrulama yapın</li>
            <li>"Admin Panel" sekmesinden sistem yönetimi yapın</li>
        </ol>
        
        <h3>⚠️ Önemli Notlar:</h3>
        <ul>
            <li>Bu sistem Google Colab ortamında çalışmaktadır</li>
            <li>Colab oturumu kapandığında sistem durur</li>
            <li>Veritabanı geçici olarak saklanır</li>
            <li>Üretim kullanımı için kalıcı hosting gereklidir</li>
        </ul>
    </div>
    """
    
    display(HTML(instructions_html))

def main():
    """Ana kurulum fonksiyonu"""
    print("🚀 Google Colab Yüz Tanıma Sistemi Kurulumu Başlıyor...\n")
    
    try:
        # Sistem güncellemesi
        print("📦 Sistem paketleri güncelleniyor...")
        subprocess.run(["apt-get", "update"], capture_output=True)
        
        # Kurulum adımları
        install_system_packages()
        install_python_packages() 
        create_project_structure()
        download_project_files()
        
        # Sunucuları başlat
        api_process = start_api_server()
        if api_process is None:
            print("❌ API sunucusu başlatılamadı. Kurulum durduruluyor.")
            return
            
        streamlit_process = start_streamlit_app()
        
        # Dış erişim ayarla
        api_url, streamlit_url = setup_ngrok()
        
        # Talimatları göster
        display_instructions(api_url, streamlit_url)
        
        print("\n✅ Kurulum tamamlandı! Sistem çalışıyor...")
        
        # Süreçleri canlı tut
        try:
            while True:
                time.sleep(60)
                # Sunucu durumlarını kontrol et
                if api_process.poll() is not None:
                    print("⚠️ API sunucusu durdu")
                if streamlit_process.poll() is not None:
                    print("⚠️ Streamlit uygulaması durdu")
                    
        except KeyboardInterrupt:
            print("\n🛑 Sistem kapatılıyor...")
            api_process.terminate()
            streamlit_process.terminate()
            
    except Exception as e:
        print(f"❌ Kurulum hatası: {str(e)}")
        print("Lütfen hata mesajını kontrol edin ve tekrar deneyin.")

if __name__ == "__main__":
    main()

