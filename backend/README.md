# DropSpot Backend Service

Drop yönetimi, waitlist ve claim işlemleri için backend servisi.

## Özellikler

- Drop CRUD işlemleri (Admin)
- Waitlist yönetimi
- Claim işlemleri
- Konum tabanlı doğrulama
- Transaction ve lock mekanizması ile idempotent işlemler
- Alembic ile veritabanı migration'ları
- Seed-based claim code üretimi

## Teknolojiler

- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Alembic (Migration)
- Geopy (Konum hesaplamaları)

## Klasör Yapısı

```
backend/
├── main.py                 # FastAPI uygulaması
├── database.py             # Database bağlantısı
├── models.py               # SQLAlchemy modelleri
├── schemas.py              # Pydantic şemaları
├── routers/
│   ├── drops.py           # Drop endpoints
│   ├── waitlist.py        # Waitlist endpoints
│   ├── claim.py           # Claim endpoints
│   ├── admin.py           # Admin CRUD endpoints
│   └── superadmin.py      # Super admin panel endpoints
├── utils/
│   ├── security.py        # JWT ve güvenlik fonksiyonları
│   └── seed_manager.py    # Seed-based code üretimi
├── alembic/               # Database migration'ları
│   ├── env.py
│   └── versions/
├── scripts/
│   ├── generate_test_data.py  # Test verisi oluşturma
│   └── add_images_to_drops.py # Drop'lara resim ekleme
├── requirements.txt       # Python bağımlılıkları
└── Dockerfile            # Docker image tanımı
```

## Kurulum

### Docker ile Çalıştırma

```bash
# Backend service'i başlat
docker-compose up -d backend

# Logları izle
docker-compose logs -f backend
```

### Manuel Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment değişkenlerini ayarla
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dropspot_db
export SECRET_KEY=your-secret-key-here
export AUTH_SERVICE_URL=http://localhost:8001

# Migration'ları çalıştır
alembic upgrade head

# Servisi başlat
uvicorn main:app --host 0.0.0.0 --port 8002
```

## API Endpoints

### Drops

#### GET /api/drops
Tüm aktif drop'ları listele

Response:
```json
[
  {
    "id": 1,
    "title": "Premium Tişört",
    "description": "Sınırlı sayıda premium tişört",
    "total_quantity": 50,
    "remaining_quantity": 48,
    "start_time": "2024-11-07T10:00:00Z",
    "end_time": "2024-11-07T18:00:00Z",
    "status": "ACTIVE"
  }
]
```

#### GET /api/drops/{drop_id}
Drop detayı

#### POST /api/drops/{drop_id}/join
Waitlist'e katıl (Case formatı)

Request Body:
```json
{
  "latitude": 41.0082,
  "longitude": 28.9784
}
```

#### POST /api/drops/{drop_id}/leave
Waitlist'ten ayrıl (Case formatı)

#### POST /api/drops/{drop_id}/claim
Claim yap (Case formatı)

Request Body:
```json
{
  "latitude": 41.0082,
  "longitude": 28.9784
}
```

### Waitlist

#### POST /api/waitlist/join
Waitlist'e katıl

#### DELETE /api/waitlist/leave/{drop_id}
Waitlist'ten ayrıl

#### GET /api/waitlist/my-waitlist
Kullanıcının waitlist'leri

### Claims

#### POST /api/claims
Claim oluştur

#### GET /api/claims/my-claims
Kullanıcının claim'leri

#### POST /api/claims/{claim_id}/verify
Claim doğrula

### Admin

#### POST /api/admin/drops
Yeni drop oluştur (Admin gerekli)

#### PUT /api/admin/drops/{drop_id}
Drop güncelle (Admin gerekli)

#### DELETE /api/admin/drops/{drop_id}
Drop sil (Admin gerekli)

#### GET /api/admin/claims
Tüm claim'leri listele (Admin gerekli)

#### GET /api/admin/stats
Platform istatistikleri (Admin gerekli)

## Transaction ve Lock Mekanizması

Kritik işlemler (waitlist join, claim) için pessimistic locking kullanılır:

1. Drop kaydı lock'lanır (`with_for_update()`)
2. Validasyonlar yapılır
3. Mevcut kayıt kontrolü (idempotency)
4. Yeni kayıt oluşturulur veya stok güncellenir
5. Commit (lock serbest bırakılır)

Bu sayede:
- Race condition'lar önlenir
- Stok kontrolü her zaman güncel bilgiyi kullanır
- Duplicate kayıt oluşmaz
- Veri bütünlüğü korunur

## Database Unique Constraints

- Waitlist: `(drop_id, user_id)` unique constraint
- Claim: `(drop_id, user_id)` unique constraint

Bu constraint'ler sayesinde aynı kullanıcı aynı drop için birden fazla waitlist/claim kaydı oluşturamaz.

## Seed-Based Sistem

Claim code ve priority score üretimi için projeye özgü seed kullanılır:

```
SEED = SHA256(GITHUB_URL | FIRST_COMMIT_EPOCH | PROJECT_START_TIME)[:12]
```

Her kullanıcı için benzersiz claim code üretilir: `DC-XXXX-XXXX`

## Migration'lar

Alembic ile veritabanı migration'ları yönetilir:

```bash
# Yeni migration oluştur
alembic revision --autogenerate -m "migration description"

# Migration'ları uygula
alembic upgrade head

# Migration'ı geri al
alembic downgrade -1
```

Servis başlatıldığında migration'lar otomatik olarak çalıştırılır.

## Konfigürasyon

Environment değişkenleri:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/dropspot_db

# Security
SECRET_KEY=your-secret-key-change-in-production

# Services
AUTH_SERVICE_URL=http://auth_service:8000

# Server
PORT=8002
ENVIRONMENT=development

# Seed Configuration
GITHUB_REPO_URL=https://github.com/TarikYil/DropSpot.git
FIRST_COMMIT_EPOCH=1762501718
PROJECT_START_TIME=202411051428
```

## Veritabanı Modelleri

### Drop
- id, title, description, image_url
- total_quantity, claimed_quantity, remaining_quantity
- latitude, longitude, address, radius_meters
- start_time, end_time
- status (ACTIVE, COMPLETED, CANCELLED)
- is_active, created_by
- created_at, updated_at

### Waitlist
- id, drop_id, user_id
- is_notified, notified_at
- created_at
- Unique Constraint: (drop_id, user_id)

### Claim
- id, drop_id, user_id
- status (PENDING, APPROVED, REJECTED)
- quantity, claim_latitude, claim_longitude, distance_from_drop
- verification_code, is_verified, verified_at
- created_at, updated_at
- Unique Constraint: (drop_id, user_id)

## Scripts

### generate_test_data.py
Test verisi oluşturur

```bash
python scripts/generate_test_data.py
```

### add_images_to_drops.py
Drop'lara resim URL'leri ekler

```bash
python scripts/add_images_to_drops.py
```

## Port

Backend service `http://localhost:8002` adresinde çalışır.

## API Dokümantasyonu

Swagger UI: http://localhost:8002/docs
ReDoc: http://localhost:8002/redoc
