# Alembic Migrations

Bu klasör Alembic migration dosyalarını içerir.

## Migration Kullanımı

### Migration Çalıştırma

```bash
# Tüm migration'ları uygula
cd backend
alembic upgrade head

# Belirli bir revision'a git
alembic upgrade <revision_id>

# Son migration'ı geri al
alembic downgrade -1

# Migration durumunu kontrol et
alembic current

# Migration geçmişini görüntüle
alembic history
```

### Yeni Migration Oluşturma

```bash
# Otomatik migration oluştur (değişiklikleri algılar)
alembic revision --autogenerate -m "Migration açıklaması"

# Manuel migration oluştur
alembic revision -m "Migration açıklaması"
```

### Docker İçinde Migration Çalıştırma

```bash
# Backend container'ı içinde
docker-compose exec backend alembic upgrade head

# Veya backend klasöründen
docker-compose exec backend bash -c "cd /app && alembic upgrade head"
```

## Mevcut Migration'lar

- **4d4f672efad2**: Add unique constraints for waitlist and claim
  - `waitlist` tablosuna `(drop_id, user_id)` unique constraint eklendi
  - `claims` tablosuna `(drop_id, user_id)` unique constraint eklendi

## Notlar

- Migration dosyaları git'e commit edilmelidir
- Production'da migration'ları çalıştırmadan önce backup alın
- Migration'ları test ortamında önce test edin

