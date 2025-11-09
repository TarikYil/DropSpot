# DropSpot - Sınırlı Stok ve Bekleme Listesi Platformu

**Proje Başlama Zamanı:** 2024-11-05 14:28:38 (İlk commit: 1762501718)

## 1. Proje Özeti ve Mimari Açıklama

DropSpot, özel ürünlerin veya etkinliklerin sınırlı stokla yayımlandığı bir platformdur. Kullanıcılar drop'lara kayıt olabilir, bekleme listesine katılabilir ve "claim window" zamanı geldiğinde sırayla hak kazanırlar.

### Mimari Yapı

Proje mikroservis mimarisi ile geliştirilmiştir:

- **Auth Service** (Port 8001): Kullanıcı kimlik doğrulama, JWT token yönetimi, rol ve yetki yönetimi
- **Backend Service** (Port 8002): Drop yönetimi, waitlist, claim işlemleri
- **AI Service** (Port 8004): Gemini tabanlı RAG chatbot servisi
- **Frontend** (Port 3000): React + Vite ile geliştirilmiş kullanıcı arayüzü
- **PostgreSQL**: Veritabanı (auth_db ve dropspot_db)

### Teknoloji Stack

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Alembic (Migration)

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios

**AI:**
- Google Gemini Pro
- RAG (Retrieval Augmented Generation)

## 2. Veri Modeli ve Endpoint Listesi

### Veri Modeli

**Drop Tablosu:**
- id, title, description, image_url
- total_quantity, claimed_quantity, remaining_quantity
- latitude, longitude, address, radius_meters
- start_time, end_time
- status (ACTIVE, COMPLETED, CANCELLED)
- is_active, created_by
- created_at, updated_at

**Waitlist Tablosu:**
- id, drop_id, user_id
- is_notified, notified_at
- created_at
- Unique Constraint: (drop_id, user_id)

**Claim Tablosu:**
- id, drop_id, user_id
- status (PENDING, APPROVED, REJECTED)
- quantity, claim_latitude, claim_longitude, distance_from_drop
- verification_code, is_verified, verified_at
- created_at, updated_at
- Unique Constraint: (drop_id, user_id)

### API Endpoint'leri

**Auth Service (Port 8001):**
- POST /api/auth/register - Kullanıcı kaydı
- POST /api/auth/login - Giriş yap
- POST /api/auth/refresh - Token yenile
- GET /api/auth/me - Kullanıcı bilgileri

**Backend Service (Port 8002):**

**Drops:**
- GET /api/drops - Tüm aktif drop'ları listele
- GET /api/drops/{drop_id} - Drop detayı
- POST /api/drops/{drop_id}/join - Waitlist'e katıl (Case formatı)
- POST /api/drops/{drop_id}/leave - Waitlist'ten ayrıl (Case formatı)
- POST /api/drops/{drop_id}/claim - Claim yap (Case formatı)

**Admin:**
- POST /api/admin/drops - Yeni drop oluştur
- PUT /api/admin/drops/{drop_id} - Drop güncelle
- DELETE /api/admin/drops/{drop_id} - Drop sil
- GET /api/admin/claims - Tüm claim'leri listele
- GET /api/admin/stats - Platform istatistikleri

**Waitlist:**
- POST /api/waitlist/join - Waitlist'e katıl
- DELETE /api/waitlist/leave/{drop_id} - Waitlist'ten ayrıl
- GET /api/waitlist/my-waitlist - Kullanıcının waitlist'leri

**Claims:**
- POST /api/claims - Claim oluştur
- GET /api/claims/my-claims - Kullanıcının claim'leri
- POST /api/claims/{claim_id}/verify - Claim doğrula

## 3. CRUD Modülü Açıklaması

Admin CRUD modülü `/api/admin` prefix'i altında yer alır ve sadece admin yetkisine sahip kullanıcılar tarafından erişilebilir.

### Drop CRUD İşlemleri

**Create (POST /api/admin/drops):**
- Yeni drop oluşturma
- Tüm zorunlu alanların validasyonu
- Zaman kontrolü (end_time > start_time)
- Admin yetkisi kontrolü

**Read (GET /api/drops):**
- Tüm aktif drop'ları listeleme
- Filtreleme (status, pagination)
- Drop detayı getirme

**Update (PUT /api/admin/drops/{drop_id}):**
- Drop bilgilerini güncelleme
- Stok miktarını güncelleme (remaining_quantity otomatik hesaplanır)
- Durum değiştirme
- Admin yetkisi kontrolü

**Delete (DELETE /api/admin/drops/{drop_id}):**
- Soft delete (is_active = False)
- İlişkili waitlist ve claim kayıtları korunur
- Admin yetkisi kontrolü

### Yetkilendirme

Admin yetkisi kontrolü `require_admin` dependency'si ile yapılır. Bu dependency:
- JWT token'ı doğrular
- Kullanıcının admin rolüne sahip olup olmadığını kontrol eder
- Yetkisiz erişimde 403 Forbidden döner

## 4. Idempotency Yaklaşımı ve Transaction Yapısı

### Idempotency

Tüm kritik işlemler idempotent olarak tasarlanmıştır:

**Waitlist Join:**
- Aynı kullanıcı aynı drop'a birden fazla kez katılamaz
- Veritabanı seviyesinde unique constraint: `(drop_id, user_id)`
- Tekrar istekte mevcut kayıt döndürülür

**Claim:**
- Aynı kullanıcı aynı drop için birden fazla claim yapamaz
- Veritabanı seviyesinde unique constraint: `(drop_id, user_id)`
- Tekrar istekte mevcut claim döndürülür

### Transaction ve Lock Mekanizması

Race condition'ları önlemek için pessimistic locking kullanılmıştır:

**Pessimistic Locking:**
```python
# Drop kaydı lock'lanır
drop = db.query(Drop).filter(Drop.id == drop_id).with_for_update().first()
```

**Transaction Yapısı:**
1. Drop kaydı lock'lanır (`with_for_update()`)
2. Validasyonlar yapılır (aktif mi, zamanı geldi mi, stok var mı)
3. Mevcut kayıt kontrolü (idempotency)
4. Yeni kayıt oluşturulur veya stok güncellenir
5. Commit (lock serbest bırakılır)

**Hata Yönetimi:**
- IntegrityError yakalanır (unique constraint violation)
- Rollback yapılır
- Mevcut kayıt döndürülür (idempotent yanıt)

**Örnek Akış (Claim):**
```
1. Transaction başlat
2. Drop'u lock'la
3. Drop kontrolü (aktif, zaman, stok)
4. Waitlist kontrolü
5. Mevcut claim kontrolü (idempotent)
6. Stok kontrolü (lock altında - güncel bilgi)
7. Claim oluştur + Stok güncelle (atomic)
8. Commit (lock serbest)
```

Bu yaklaşım sayesinde:
- Aynı anda gelen birden fazla request sırayla işlenir
- Stok kontrolü her zaman güncel bilgiyi kullanır
- Duplicate kayıt oluşmaz
- Veri bütünlüğü korunur

## 5. Kurulum Adımları

### Gereksinimler

- Docker ve Docker Compose
- Git

### Otomatik Kurulum

Proje GitHub'dan çekilip build alındığında tüm veritabanları ve tablolar otomatik olarak oluşturulur:

1. Projeyi klonlayın:
```bash
git clone https://github.com/TarikYil/DropSpot.git
cd DropSpot
```

2. Docker container'larını başlatın:
```bash
docker-compose up -d
```

**Otomatik Oluşturulanlar:**
- PostgreSQL veritabanları (auth_db, dropspot_db, test_auth_db, test_dropspot_db)
- Tüm tablolar (Base.metadata.create_all ile)
- Alembic migration'ları (backend service startup'ında otomatik çalışır)
- Default admin kullanıcısı (auth service startup'ında otomatik oluşturulur)

**Default Admin Bilgileri:**
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`

### Manuel Kurulum (Opsiyonel)

Eğer manuel olarak migration çalıştırmak isterseniz:

```bash
# Backend migration'ları
docker-compose exec backend alembic upgrade head

# Default admin oluşturma
docker-compose exec auth_service python scripts/create_default_admin.py
```

### AI Service Kurulumu

AI Service için Gemini API key'i gereklidir. `.env` dosyası oluşturmanız gerekir:

1. `ai_service` klasörüne gidin:
```bash
cd ai_service
```

2. `.env.example` dosyasını `.env` olarak kopyalayın:
```bash
cp .env.example .env
```

3. `.env` dosyasını düzenleyin ve Gemini API key'inizi ekleyin:
```bash
# .env dosyasını bir metin editörü ile açın
# Windows: notepad .env
# Linux/Mac: nano .env veya vim .env
```

4. `.env` dosyası içeriği:
```env
# Gemini API Key (Zorunlu)
# Google AI Studio'dan ücretsiz alabilirsiniz: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Gemini Model (Opsiyonel - varsayılan: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# Server Port (Opsiyonel - varsayılan: 8004)
PORT=8004

# Environment (Opsiyonel - varsayılan: development)
ENVIRONMENT=development

# Service URLs (Docker içinde otomatik ayarlanır)
AUTH_SERVICE_URL=http://auth_service:8000
BACKEND_SERVICE_URL=http://backend:8002

# RAG Settings (Opsiyonel)
MAX_CONTEXT_LENGTH=4000
MAX_CHAT_HISTORY=10
TEMPERATURE=0.7
TOP_P=0.95
TOP_K=40

# Security (Opsiyonel)
SECRET_KEY=dropspot-ai-secret-key-2024
```

5. Gemini API Key alma:
   - [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin
   - Google hesabınızla giriş yapın
   - "Create API Key" butonuna tıklayın
   - Oluşturulan API key'i kopyalayın ve `.env` dosyasındaki `GEMINI_API_KEY` değerine yapıştırın

**Not:** `.env` dosyası Git'e commit edilmez (`.gitignore`'da tanımlıdır). Her geliştirici kendi API key'ini oluşturmalıdır.

### Frontend Kurulumu

Frontend Docker ile otomatik olarak başlatılır. Manuel kurulum için:

```bash
cd frontend
npm install
npm run dev
```

Frontend `http://localhost:3000` adresinde çalışır.

### Servisler

- Auth Service: http://localhost:8001
- Backend Service: http://localhost:8002
- AI Service: http://localhost:8004
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

### API Dokümantasyonu

- Auth Service Swagger: http://localhost:8001/docs
- Backend Service Swagger: http://localhost:8002/docs
- AI Service Swagger: http://localhost:8004/docs

## 6. Ekran Görüntüleri
<img width="1916" height="910" alt="image" src="https://github.com/user-attachments/assets/7c98ceeb-7d49-400c-ba49-3bc15e73fd44" />

### Ana Sayfa (Drop Listesi)
Ana sayfada tüm aktif drop'lar listelenir. Kullanıcılar drop'lara göz atabilir, arama yapabilir ve bekleme listesine katılabilir. Her drop kartında ürün görseli, başlık, açıklama, stok bilgisi ve konum bilgisi görüntülenir.

**Özellikler:**
- Drop kartları grid layout ile gösterilir
- Arama ve filtreleme özellikleri
- Stok durumu görsel olarak gösterilir
- Responsive tasarım (mobil uyumlu)

### Drop Detay Sayfası
<img width="1918" height="908" alt="Ekran görüntüsü 2025-11-09 175049" src="https://github.com/user-attachments/assets/0d40537c-c2c9-45e1-8bfa-31a9a0ebad49" />

Kullanıcılar drop detay sayfasında ürün hakkında detaylı bilgi görüntüleyebilir. Sayfada ürün görseli, açıklama, stok durumu, bekleme listesi sayısı, konum bilgisi ve zaman bilgisi yer alır.

**Özellikler:**
- Büyük ürün görseli
- Stok durumu ve progress bar
- Bekleme listesi sayısı
- Konum bilgisi ve mesafe kontrolü
- Başlangıç ve bitiş zamanı
- Claim window açıldığında claim butonu aktif olur
- Konum kontrolü ile claim yapılabilir

**Örnek Görüntü:**
- Sol tarafta büyük ürün görseli (örn: Nike Air Force 1 x Carhartt WIP)
- Sağ tarafta ürün detayları:
  - Başlık: "Exclusive Hoodie Drop #2"
  - Stok: 48/64 (progress bar ile)
  - Bekleme Listesi: 6 kişi bekliyor
  - Konum: Beşiktaş, İstanbul (mesafe bilgisi ile)
  - Zaman: Başlangıç ve bitiş tarihleri

### Bekleme Listem Sayfası
<img width="1914" height="910" alt="Ekran görüntüsü 2025-11-09 174853" src="https://github.com/user-attachments/assets/98421f53-db1c-4512-b95f-67f58ef0af08" />

Kullanıcılar bu sayfada bekleme listesine ekledikleri drop'ları görüntüleyebilir. Her drop için sıra numarası, ürün görseli, başlık, stok durumu, konum ve tarih bilgisi gösterilir.

**Özellikler:**
- Grid layout ile drop kartları
- Her drop için sıra numarası (örn: "Sıra: 1")
- Drop detaylarına gitme butonu
- Bekleme listesinden çıkarma butonu
- Stok durumu takibi

**Örnek Görüntü:**
- 2 satır, 3 sütun grid layout
- Her kartta:
  - Sıra numarası badge'i
  - Ürün görseli
  - Başlık ve açıklama
  - Stok bilgisi (örn: "Stok: 139/148")
  - Konum (örn: "Beyoğlu, İstanbul")
  - Tarih (örn: "16.11.2025")
  - "Detay →" butonu
  - Çıkış (X) butonu

### Claim'lerim Sayfası
<img width="1914" height="910" alt="Ekran görüntüsü 2025-11-09 174853" src="https://github.com/user-attachments/assets/980ed5c9-fb7e-47c0-a16a-4e2bcf0f9b23" />

Kullanıcılar bu sayfada yaptıkları claim'leri görüntüleyebilir. Her claim için durum (Onaylandı/Reddedildi/Beklemede), ürün görseli, başlık, verification code ve tarih bilgisi gösterilir.

**Özellikler:**
- Durum badge'leri (yeşil: Onaylandı, kırmızı: Reddedildi)
- Ürün görselleri
- Verification code bilgisi
- Claim tarihi
- Drop detaylarına gitme butonu

**Örnek Görüntü:**
- Grid layout ile claim kartları
- Her kartta:
  - Durum badge'i (üst sağ köşede)
  - Ürün görseli
  - Başlık ve açıklama
  - Miktar: 1
  - Kod: CODE-2-6-9526
  - Tarih: 07.11.2025
  - "Drop Detayı →" butonu

**Durum Örnekleri:**
- Onaylandı: Yeşil badge, checkmark ikonu
- Reddedildi: Kırmızı badge, X ikonu
- Beklemede: Sarı badge (varsayılan)

### Admin Paneli - Drop'lar Sekmesi
<img width="1916" height="907" alt="Ekran görüntüsü 2025-11-09 174828" src="https://github.com/user-attachments/assets/9d76f187-bd92-47a7-9303-df7cae828869" />

Admin kullanıcıları bu sayfada drop'ları yönetebilir. İstatistik kartları, drop listesi tablosu ve yeni drop oluşturma butonu bulunur.

**Özellikler:**
- İstatistik kartları:
  - Toplam Drop sayısı
  - Aktif Drop sayısı
  - Toplam Claim sayısı
  - Waitlist sayısı
- Drop listesi tablosu:
  - Başlık, Stok, Durum, İşlemler kolonları
  - Her drop için düzenleme ve silme butonları
  - Durum badge'leri (aktif/pasif)
- "+ Yeni Drop" butonu ile yeni drop oluşturma

**Örnek Görüntü:**
- Üst kısımda "Admin Paneli" başlığı ve "+ Yeni Drop" butonu
- İstatistik kartları (4 adet):
  - Toplam Drop: 8
  - Aktif Drop: 3
  - Toplam Claim: 24
  - Waitlist: 61
- Tablo başlıkları: Başlık, Stok, Durum, İşlemler
- Tablo satırları:
  - "Sınırlı Stoklu Ürün #4" - Stok: 169/181 - Durum: active (yeşil) - Düzenle/Sil
  - "Exclusive Hoodie Drop #1" - Stok: 43/71 - Durum: active (yeşil) - Düzenle/Sil
  - "Exclusive Hoodie Drop #2" - Stok: 48/64 - Durum: active (yeşil) - Düzenle/Sil

### Admin Paneli - Claim'ler Sekmesi
![Uploading Ekran görüntüsü 2025-11-09 174853.png…]()

Admin kullanıcıları bu sayfada tüm claim'leri görüntüleyebilir ve yönetebilir. Claim'ler durumlarına göre filtrelenebilir.

**Özellikler:**
- Durum filtreleme butonları:
  - Beklemede (Pending)
  - Onaylandı (Approved) - aktif
  - Reddedildi (Rejected)
- Claim listesi tablosu:
  - ID, Drop ID, Kullanıcı ID, Miktar, Durum, Tarih, İşlemler kolonları
  - Durum badge'leri
  - Onaylama/Reddetme işlemleri

**Örnek Görüntü:**
- "Claim'ler" sekmesi aktif (mavi alt çizgi)
- Filtre butonları: Beklemede (gri), Onaylandı (mavi, aktif), Reddedildi (gri)
- Tablo başlıkları: ID, Drop ID, Kullanıcı ID, Miktar, Durum, Tarih, İşlemler
- Tablo satırları:
  - #6, #2, #6, 1, Onaylandı (yeşil badge), 07.11.2025
  - #7, #3, #1, 1, Onaylandı (yeşil badge), 07.11.2025
  - #12, #4, #10, 1, Onaylandı (yeşil badge), 07.11.2025

### Süper Admin Paneli
<img width="1914" height="907" alt="image" src="https://github.com/user-attachments/assets/e3fb179f-0b67-48d5-8b49-1cb9f56980be" />

Süper admin kullanıcıları bu sayfada kullanıcıları ve rollerini yönetebilir. Kullanıcı listesi, rol atama ve yetki yönetimi özellikleri bulunur.
<img width="1913" height="907" alt="image" src="https://github.com/user-attachments/assets/939eb697-7984-4216-9c1e-c8055ae43c94" />

**Özellikler:**
- Kullanıcı listesi tablosu
- Rol atama işlemleri
- Kullanıcı durumu yönetimi (aktif/pasif)
- Yetki yönetimi

### Ayarlar Sayfası
Kullanıcılar bu sayfada profil bilgilerini görüntüleyebilir ve güncelleyebilir.

**Özellikler:**
- Profil bilgileri (ad, email, kullanıcı adı)
- Şifre değiştirme
- Hesap ayarları

### AI Chatbot Widget
Sağ alt köşede bulunan chatbot widget'ı ile kullanıcılar platform hakkında sorular sorabilir.

**Özellikler:**
- Sağ alt köşede sabit konum
- Mor renkli chat bubble ikonu
- Tıklanınca açılan chat penceresi
- Platform bilgileri hakkında AI destekli yanıtlar

## 7. Teknik Tercihler ve Kişisel Katkılar

### Teknik Tercihler

**Mikroservis Mimarisi:**
- Servislerin bağımsız ölçeklenebilirliği
- Teknoloji bağımsızlığı
- Hata izolasyonu

**PostgreSQL:**
- ACID uyumluluğu
- Transaction desteği
- Unique constraint'ler ile veri bütünlüğü

**FastAPI:**
- Yüksek performans
- Otomatik API dokümantasyonu
- Type hints ile tip güvenliği

**React + Vite:**
- Hızlı geliştirme ortamı
- Modern React özellikleri
- Optimize build süreci

### Kişisel Katkılar

**Transaction ve Lock Mekanizması:**
- Pessimistic locking ile race condition önleme
- Atomic işlemler ile veri bütünlüğü
- Idempotent API tasarımı

**Seed-Based Sistem:**
- Projeye özgü benzersiz seed üretimi
- Tekrarlanabilir rastgelelik
- Claim code üretimi

**AI Entegrasyonu:**
- Gemini Pro ile RAG sistemi
- Context-aware chatbot
- Kullanıcıya özel bilgi sağlama

**Test Altyapısı:**
- Unit testler
- Integration testler
- Frontend component testleri
- Docker-based test ortamı

**Migration Sistemi:**
- Alembic ile veritabanı versiyonlama
- Otomatik migration uygulama (startup'ta)
- Rollback desteği

**Otomatik Kurulum:**
- Docker Compose ile tek komutla kurulum
- Veritabanlarının otomatik oluşturulması
- Migration'ların otomatik çalıştırılması
- Default admin kullanıcısının otomatik oluşturulması

## 8. Seed Üretim Yöntemi ve Proje İçindeki Kullanımı

### Seed Hesaplama

Seed, projeye özgü benzersiz bir değerdir ve şu formülle hesaplanır:

```
SEED = SHA256(GITHUB_URL | FIRST_COMMIT_EPOCH | PROJECT_START_TIME)[:12]
```

**Hesaplama Adımları:**
1. GitHub remote URL: `https://github.com/TarikYil/DropSpot.git`
2. İlk commit epoch: `1762501718`
3. Proje başlama zamanı: `202411051428` (YYYYMMDDHHmm formatında)
4. Bu değerler birleştirilir: `{url}|{epoch}|{start_time}`
5. SHA256 hash alınır ve ilk 12 karakteri seed olarak kullanılır

### Seed Kullanımı

**Claim Code Üretimi:**
```python
verification_code = seed_manager.generate_claim_code(
    user_id=user_id,
    drop_id=drop_id,
    timestamp=now
)
```

Her kullanıcı için benzersiz claim code üretilir. Format: `DC-XXXX-XXXX`

**Priority Score Hesaplama:**
```python
priority_score = seed_manager.calculate_priority_score(
    user_id=user_id,
    drop_id=drop_id,
    waitlist_position=position
)
```

Waitlist sıralaması için öncelik skoru hesaplanır. Bu skor:
- Seed'e dayalı rastgele bileşen içerir
- Waitlist pozisyonunu dikkate alır
- Tekrarlanabilir ve adildir

### Seed Yönetimi

Seed değeri `SeedManager` sınıfı tarafından yönetilir ve environment variable'lardan alınabilir:
- `GITHUB_REPO_URL`: GitHub repository URL
- `FIRST_COMMIT_EPOCH`: İlk commit zamanı (epoch)
- `PROJECT_START_TIME`: Proje başlama zamanı (YYYYMMDDHHmm)

## 9. Bonus: AI Entegrasyonu

### Gemini Tabanlı RAG Chatbot

Projeye Google Gemini Pro tabanlı bir AI chatbot servisi entegre edilmiştir.

**Özellikler:**
- RAG (Retrieval Augmented Generation) sistemi
- Backend'den gerçek zamanlı veri çekme
- Kullanıcıya özel bilgi sağlama (token ile)
- Chat history desteği
- Context-aware yanıtlar

**Kullanım:**
- Frontend'de sağ alt köşede chatbot widget'ı
- Kullanıcılar drop'lar, waitlist, claim süreçleri hakkında soru sorabilir
- AI, platform bilgilerini kullanarak yanıt verir

**API Endpoint:**
- POST /api/chat/ask - Soru sor
- Token ile kullanıcıya özel bilgiler
- Token olmadan genel platform bilgileri

**Örnek Kullanım:**
```
Kullanıcı: "Aktif drop'lar neler?"
AI: "Şu anda 3 aktif drop var:
1. Premium Tişört - Stok: 48/50
2. Limited Edition Ayakkabı - Stok: 12/20
..."
```

## Test ve Kalite

### Test Kapsamı

**Backend:**
- Unit testler: Auth utils, password hashing, token işlemleri
- Integration testler: API endpoint'leri, idempotency testleri

**Frontend:**
- Component testleri: Home, DropDetail
- E2E smoke testleri

**Test Çalıştırma:**
```bash
# Backend testleri
docker-compose run --rm test_service pytest tests/ -v

# Frontend testleri
cd frontend
npm test
```

## Güvenlik

- JWT token tabanlı kimlik doğrulama
- Argon2 şifre hash'leme
- CORS yapılandırması
- SQL injection koruması (SQLAlchemy ORM)
- XSS koruması (React)
- Environment variable'lar ile hassas bilgi yönetimi

## Branch Yapısı

Proje servis bazlı branch yapısına sahiptir:

- `main` - Tüm servislerin birleştiği ana branch
- `feature/auth-service` - Auth servisi geliştirmeleri
- `feature/backend-service` - Backend servisi geliştirmeleri
- `feature/frontend` - Frontend geliştirmeleri
- `feature/ai-service` - AI servisi geliştirmeleri
- `feature/test-service` - Test altyapısı geliştirmeleri
- `feature/database-migrations` - Veritabanı migration'ları

Her servis kendi branch'inde bağımsız geliştirilir ve main'e merge edilir.


