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

### Drop Listesi Sayfası
Ana sayfada tüm aktif drop'lar listelenir. Kullanıcılar drop'lara göz atabilir, arama yapabilir ve bekleme listesine katılabilir.

### Claim Ekranı
Kullanıcılar claim window açıldığında drop detay sayfasından claim yapabilir. Konum kontrolü yapılır ve verification code oluşturulur.

### Admin Panel
Admin kullanıcıları drop'ları oluşturabilir, güncelleyebilir ve silebilir. Ayrıca tüm claim'leri görüntüleyebilir ve onaylayabilir.

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


