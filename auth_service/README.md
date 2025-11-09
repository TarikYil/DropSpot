# DropSpot Auth Service

Kullanıcı kimlik doğrulama, JWT token yönetimi ve rol/yetki yönetimi servisi.

## Özellikler

- Kullanıcı kaydı ve girişi
- JWT access token ve refresh token yönetimi
- Rol ve yetki sistemi (Admin, User, Superuser)
- Argon2 şifre hash'leme
- Token yenileme mekanizması
- Default admin kullanıcısı otomatik oluşturma

## Teknolojiler

- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Argon2 (Password Hashing)
- JWT (JSON Web Tokens)

## Klasör Yapısı

```
auth_service/
├── main.py                 # FastAPI uygulaması
├── database.py             # Database bağlantısı
├── models.py               # SQLAlchemy modelleri
├── schemas.py              # Pydantic şemaları
├── routers/
│   ├── auth.py            # Authentication endpoints
│   └── roles.py           # Rol yönetimi endpoints
├── utils/
│   └── auth_utils.py      # Auth yardımcı fonksiyonları
├── scripts/
│   ├── create_default_admin.py  # Default admin oluşturma
│   ├── make_superuser.py        # Kullanıcıyı superuser yapma
│   └── reset_password.py        # Şifre sıfırlama
├── requirements.txt       # Python bağımlılıkları
└── Dockerfile            # Docker image tanımı
```

## Kurulum

### Docker ile Çalıştırma

```bash
# Auth service'i başlat
docker-compose up -d auth_service

# Logları izle
docker-compose logs -f auth_service
```

### Manuel Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment değişkenlerini ayarla
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/auth_db
export SECRET_KEY=your-secret-key-here

# Servisi başlat
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

#### POST /api/auth/register
Kullanıcı kaydı

Request Body:
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "SecurePass123",
  "full_name": "Test User"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false
}
```

#### POST /api/auth/login
Kullanıcı girişi

Request Body:
```json
{
  "username": "testuser",
  "password": "SecurePass123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "is_active": true,
    "is_superuser": false
  }
}
```

#### POST /api/auth/refresh
Token yenileme

Request Body:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /api/auth/me
Kullanıcı bilgileri (Token gerekli)

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true
}
```

### Roles & Permissions

#### GET /api/roles
Tüm roller (Admin gerekli)

#### POST /api/roles
Yeni rol oluştur (Superuser gerekli)

#### GET /api/roles/{role_id}
Rol detayı

#### PUT /api/roles/{role_id}
Rol güncelle (Superuser gerekli)

#### DELETE /api/roles/{role_id}
Rol sil (Superuser gerekli)

## Konfigürasyon

Environment değişkenleri:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/auth_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server
PORT=8000
ENVIRONMENT=development

# Default Admin (Otomatik oluşturulur)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
ADMIN_FULL_NAME=Default Admin
```

## Default Admin Kullanıcısı

Servis ilk başlatıldığında otomatik olarak bir super admin kullanıcısı oluşturulur:

- Username: `admin` (ADMIN_USERNAME ile değiştirilebilir)
- Email: `admin@example.com` (ADMIN_EMAIL ile değiştirilebilir)
- Password: `admin123` (ADMIN_PASSWORD ile değiştirilebilir)
- Role: Superuser

Production ortamında mutlaka şifreyi değiştirin!

## Güvenlik

- Argon2 ile şifre hash'leme
- JWT token tabanlı kimlik doğrulama
- Refresh token mekanizması
- CORS yapılandırması
- SQL injection koruması (SQLAlchemy ORM)

## Veritabanı Modelleri

### User
- id, email, username, full_name
- hashed_password
- is_active, is_superuser, is_verified
- created_at, updated_at

### RefreshToken
- id, user_id, token
- expires_at, created_at

### Role
- id, name, description
- permissions (many-to-many)

### Permission
- id, name, description

## Scripts

### create_default_admin.py
Default admin kullanıcısı oluşturur

```bash
python scripts/create_default_admin.py
```

### make_superuser.py
Bir kullanıcıyı superuser yapar

```bash
python scripts/make_superuser.py <username>
```

### reset_password.py
Kullanıcı şifresini sıfırlar

```bash
python scripts/reset_password.py <username> <new_password>
```

## Port

Auth service `http://localhost:8001` adresinde çalışır (docker-compose.yml'de port mapping: 8001:8000).

## API Dokümantasyonu

Swagger UI: http://localhost:8001/docs
ReDoc: http://localhost:8001/redoc

