# Auth Service Scripts

Bu klasör auth service için yardımcı script'leri içerir.

## Script'ler

### 1. `create_default_admin.py`

Default süper admin kullanıcısı oluşturur.

**Kullanım:**
```bash
# Docker container içinde
docker-compose exec auth_service python scripts/create_default_admin.py

# Veya özelleştirilmiş parametrelerle
docker-compose exec auth_service python scripts/create_default_admin.py <username> <email> <password> <full_name>

# Environment variable'larla
ADMIN_USERNAME=myadmin ADMIN_EMAIL=admin@mydomain.com ADMIN_PASSWORD=secure123 \
docker-compose exec auth_service python scripts/create_default_admin.py
```

**Varsayılan Değerler:**
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`
- Full Name: `Default Admin`

**Not:** Bu script manuel çalıştırma için. Otomatik olarak auth service başlatıldığında zaten default admin oluşturulur.

### 2. `make_superuser.py`

Mevcut bir kullanıcıyı süper admin yapar.

**Kullanım:**
```bash
docker-compose exec auth_service python scripts/make_superuser.py <username_or_email>
```

**Örnek:**
```bash
docker-compose exec auth_service python scripts/make_superuser.py john@example.com
```

### 3. `reset_password.py`

Kullanıcı şifresini sıfırlar.

**Kullanım:**
```bash
docker-compose exec auth_service python scripts/reset_password.py <username_or_email> <new_password>
```

## Otomatik Default Admin Oluşturma

Auth service her başlatıldığında otomatik olarak default admin kullanıcısını kontrol eder ve yoksa oluşturur.

**Environment Variables:**
- `ADMIN_USERNAME`: Admin kullanıcı adı (default: `admin`)
- `ADMIN_EMAIL`: Admin email adresi (default: `admin@example.com`)
- `ADMIN_PASSWORD`: Admin şifresi (default: `admin123`)
- `ADMIN_FULL_NAME`: Admin tam adı (default: `Default Admin`)

**Özelleştirme:**
`.env` dosyasına veya `docker-compose.yml`'de environment variable'ları ayarlayarak özelleştirebilirsiniz:

```yaml
environment:
  ADMIN_USERNAME: myadmin
  ADMIN_EMAIL: admin@mydomain.com
  ADMIN_PASSWORD: secure_password_123
  ADMIN_FULL_NAME: My Admin User
```

**Güvenlik Uyarısı:**
⚠️ Production ortamında mutlaka:
1. Default şifreyi değiştirin
2. Güçlü bir şifre kullanın
3. Environment variable'ları güvenli bir şekilde yönetin

