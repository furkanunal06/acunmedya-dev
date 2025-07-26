# Yüz Tanıma Uygulaması - Proje Analizi ve Tasarım

## Proje Genel Bakış

Bu dokümantasyon, Google Colab ortamında çalışacak kapsamlı bir yüz tanıma uygulamasının geliştirilmesi için gerekli analiz ve tasarım sürecini içermektedir. Uygulama, modern yüz tanıma teknolojilerini kullanarak güvenli kimlik doğrulama sistemi sağlayacaktır.

## Fonksiyonel Gereksinimler Analizi

### 1. Yüz Verisi Kayıt Sistemi (Face Enrollment)

Kullanıcı yüz verilerinin ilk kez sisteme kaydedilmesi kritik bir süreçtir. Bu süreç, yüksek kaliteli ve çeşitli yüz verilerinin toplanmasını gerektirir. Sistem, kullanıcıdan minimum 10 farklı pozda yüz verisi alacak şekilde tasarlanmalıdır. Bu pozlar şunları içermelidir:

- Düz bakış (frontal view)
- Sağa 15-30 derece dönük
- Sola 15-30 derece dönük
- Hafif yukarı bakış
- Hafif aşağı bakış
- Gülümseme ifadesi
- Nötr ifade
- Farklı ışık koşulları
- Gözlük varsa gözlükle ve gözlüksüz
- Farklı mesafelerden çekim

Bu çeşitlilik, sistemin farklı koşullarda daha doğru tanıma yapabilmesini sağlayacaktır.

### 2. Canlı Yüz Algılama Sistemi

Gerçek zamanlı yüz algılama sistemi, kamera akışından sürekli olarak yüz verilerini işleyebilmelidir. Bu sistem şu özellikleri içermelidir:

- Webcam veya mobil kamera desteği
- Gerçek zamanlı video akışı işleme
- Yüz sınırlarının (bounding box) görsel gösterimi
- Yüz kalitesi değerlendirmesi (bulanıklık, ışık, açı kontrolü)
- Canlılık tespiti (liveness detection) için temel kontroller

### 3. Yüz Eşleştirme ve Benzerlik Hesaplama

Yüz eşleştirme sistemi, kayıtlı yüz verileri ile giriş yapan kişinin yüz verilerini karşılaştırarak benzerlik oranı hesaplayacaktır. Bu süreç şu adımları içerir:

- Giriş yapan kişinin yüz embedding'inin çıkarılması
- Veritabanındaki tüm kayıtlı embedding'lerle karşılaştırma
- Cosine similarity veya Euclidean distance hesaplama
- En yüksek benzerlik oranının belirlenmesi
- Eşik değeri kontrolü

### 4. Güvenlik Eşik Değeri Sistemi

Sistem, önceden belirlenmiş bir eşik değeri altında kalan benzerlik oranlarını reddetmelidir. Bu eşik değeri:

- Varsayılan olarak %85-90 arasında ayarlanmalı
- Admin panelinden değiştirilebilir olmalı
- Farklı kullanıcı grupları için farklı eşik değerleri tanımlanabilmeli
- False positive ve false negative oranlarını minimize edecek şekilde optimize edilmeli




### 5. Veri Güvenliği ve Hash'leme

Yüz verileri hassas kişisel bilgiler olduğu için güvenli bir şekilde saklanmalıdır:

- Ham yüz görüntüleri asla veritabanında saklanmamalı
- Sadece 128-boyutlu embedding vektörleri saklanmalı
- Embedding'ler ek bir hash katmanı ile korunmalı
- Veritabanı bağlantıları şifrelenmiş olmalı
- Kullanıcı kimlik bilgileri ayrı tablolarda tutulmalı

### 6. Hata Loglama Sistemi

Güvenlik açısından tüm başarısız giriş denemeleri loglanmalıdır:

- Timestamp bilgisi (UTC formatında)
- IP adresi bilgisi
- Denenen kullanıcı kimliği (varsa)
- Hata türü (yüz bulunamadı, eşik altı benzerlik, vb.)
- Benzerlik oranı
- Kullanılan kamera/cihaz bilgisi

### 7. Admin Panel Yetkileri

Admin paneli kapsamlı yönetim özellikleri sunmalıdır:

- Kullanıcı listesi görüntüleme
- Yeni kullanıcı ekleme (sadece admin)
- Kullanıcı yüz verilerini silme
- Sistem ayarları (eşik değerleri, güvenlik parametreleri)
- Hata loglarını görüntüleme ve filtreleme
- Sistem istatistikleri (başarılı/başarısız giriş oranları)

### 8. Çoklu Yüz Algılama Uyarı Sistemi

Güvenlik açısından aynı anda birden fazla yüz algılandığında sistem uyarı vermelidir:

- Kamera görüntüsünde 2 veya daha fazla yüz tespit edildiğinde uyarı
- Sadece tek kişinin giriş yapmasına izin verme
- Uyarı mesajı ile kullanıcıyı bilgilendirme
- Bu durumların loglanması

## Teknik Gereksinimler Analizi

### 1. Yüz Tanıma Modeli ve Embedding Sistemi

Sistem, modern deep learning tabanlı yüz tanıma modellerini kullanacaktır. İki ana seçenek değerlendirilmiştir:

**FaceNet Modeli:**
- Google tarafından geliştirilen
- 128-boyutlu embedding üretir
- Triplet loss fonksiyonu kullanır
- Yüksek doğruluk oranı
- Açık kaynak implementasyonları mevcut

**ArcFace Modeli:**
- Daha yeni ve gelişmiş mimari
- Additive Angular Margin Loss kullanır
- FaceNet'ten daha yüksek performans
- 512-boyutlu embedding (128'e indirgenebilir)
- Daha iyi generalization

Proje için ArcFace modeli tercih edilecek ve embedding boyutu 128'e indirgenerek optimize edilecektir.

### 2. Veritabanı Tasarımı

İki veritabanı seçeneği değerlendirilmiştir:

**MongoDB (NoSQL):**
- Embedding vektörleri için uygun
- Esnek şema yapısı
- Hızlı okuma/yazma işlemleri
- JSON formatında veri saklama
- Vector search desteği

**PostgreSQL (SQL):**
- ACID uyumluluğu
- Güçlü güvenlik özellikleri
- pgvector extension ile vector desteği
- Daha karmaşık sorgular için uygun
- Backup ve recovery özellikleri

Proje için PostgreSQL tercih edilecek çünkü güvenlik kritik bir faktördür ve ACID uyumluluğu gereklidir.

### 3. Veritabanı Şema Tasarımı

```sql
-- Kullanıcılar tablosu
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Yüz embedding'leri tablosu
CREATE TABLE face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    embedding_hash VARCHAR(256) NOT NULL,
    embedding_vector FLOAT8[] NOT NULL,
    pose_type VARCHAR(20) NOT NULL,
    quality_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Giriş logları tablosu
CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ip_address INET NOT NULL,
    success BOOLEAN NOT NULL,
    similarity_score FLOAT,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sistem ayarları tablosu
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(50) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. API Endpoint Tasarımı

RESTful API yapısı şu endpoint'leri içerecektir:

**Kimlik Doğrulama Endpoint'leri:**
- `POST /api/auth/login` - Admin girişi
- `POST /api/auth/refresh` - Token yenileme
- `POST /api/auth/logout` - Çıkış

**Yüz Tanıma Endpoint'leri:**
- `POST /api/face/enroll` - Yeni yüz kaydı
- `POST /api/face/authenticate` - Yüz ile giriş
- `GET /api/face/users` - Kayıtlı kullanıcılar
- `DELETE /api/face/user/{id}` - Kullanıcı silme

**Admin Endpoint'leri:**
- `GET /api/admin/logs` - Giriş logları
- `GET /api/admin/stats` - Sistem istatistikleri
- `PUT /api/admin/settings` - Sistem ayarları

**Sistem Endpoint'leri:**
- `GET /api/health` - Sistem durumu
- `POST /api/face/detect` - Canlı yüz algılama



### 5. API Güvenliği (JWT)

Tüm API endpoint'leri JSON Web Token (JWT) ile korunacaktır. Bu, yetkisiz erişimi engelleyecektir:

- Kullanıcı girişi sonrası JWT token üretimi
- Her istekte token doğrulama
- Refresh token mekanizması
- Token süreleri ve yenileme politikaları

### 6. Boyut İndirgeme (PCA - İsteğe Bağlı)

Embedding'ler üzerinde PCA (Principal Component Analysis) ile boyut indirgeme işlemi isteğe bağlı olarak uygulanabilir. Bu, depolama alanından tasarruf sağlayabilir ve karşılaştırma sürelerini hızlandırabilir, ancak doğruluk üzerinde etkisi dikkatlice değerlendirilmelidir.

### 7. Arayüz Teknolojisi

Basit bir arayüz için iki seçenek değerlendirilmiştir:

**Streamlit:**
- Hızlı prototipleme için ideal
- Python tabanlı, kolay entegrasyon
- Daha az frontend bilgisi gerektirir
- Canlı kamera akışı desteği

**React:**
- Daha esnek ve ölçeklenebilir
- Modern web uygulamaları için uygun
- Daha iyi UI/UX kontrolü
- Daha fazla geliştirme süresi gerektirir

Proje için hızlı geliştirme ve Google Colab uyumluluğu nedeniyle **Streamlit** tercih edilecektir.

### 8. Docker ile Konteynerizasyon

Tüm uygulama, Docker konteynerleri kullanılarak paketlenecektir. Bu, uygulamanın farklı ortamlarda (Colab dahil) kolayca dağıtılmasını ve çalıştırılmasını sağlayacaktır:

- Backend için Dockerfile
- Frontend için Dockerfile
- Veritabanı için Docker Compose
- Gerekli tüm bağımlılıkların konteyner içine dahil edilmesi

## Google Colab Entegrasyonu

Uygulama, Google Colab ortamında çalışacak şekilde tasarlanacaktır. Bu, aşağıdaki hususları içerir:

- Colab'ın GPU kaynaklarını kullanma (yüz tanıma için)
- Gerekli kütüphanelerin Colab ortamına kurulması
- Veritabanı bağlantılarının Colab ortamına uygun şekilde yapılandırılması
- Ngrok veya benzeri tünelleme servisleri ile dışarıdan erişim (API ve Streamlit için)
- Dosya sistemi yönetimi (Colab'ın geçici depolama alanı ve Google Drive entegrasyonu)

## Mimari Tasarım

```mermaid
graph TD
    A[Kullanıcı/Admin] -->|Web Tarayıcı| B(Streamlit Frontend)
    B -->|HTTP/HTTPS (JWT)| C(Flask Backend API)
    C -->|Veri İşleme| D(Yüz Tanıma Modeli - ArcFace)
    C -->|Veritabanı İşlemleri| E(PostgreSQL Veritabanı)
    D -->|Embedding| E
    C -->|Loglama| F(Log Dosyaları/Veritabanı)
    subgraph Google Colab Ortamı
        B
        C
        D
        E
        F
    end
    G[Kamera] -->|Video Akışı| B
```

## Geliştirme Ortamı ve Araçlar

- **Programlama Dili:** Python 3.9+
- **Yüz Tanıma Kütüphanesi:** `face_recognition`, `insightface` veya `dlib`
- **Web Çerçevesi:** Flask (Backend), Streamlit (Frontend)
- **Veritabanı:** PostgreSQL
- **Kimlik Doğrulama:** PyJWT
- **Konteynerizasyon:** Docker, Docker Compose
- **Geliştirme Ortamı:** Google Colab

## Sonraki Adımlar

1. Gerekli kütüphanelerin ve bağımlılıkların belirlenmesi.
2. Yüz tanıma modelinin seçimi ve entegrasyonu.
3. Veritabanı kurulumu ve şema oluşturma.
4. API endpoint'lerinin geliştirilmesi.
5. Streamlit arayüzünün tasarlanması.
6. Güvenlik katmanlarının eklenmesi.
7. Google Colab üzerinde test ve optimizasyon.
8. Kapsamlı dokümantasyon oluşturulması.


