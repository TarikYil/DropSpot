# Branch Yapısı ve Çalışma Kılavuzu

## Branch Organizasyonu

Her servis kendi branch'inde geliştirilmelidir:

### Mevcut Branch'ler

- `main` - Ana branch, production-ready kod
- `feature/auth-service` - Auth service geliştirmeleri
- `feature/backend-service` - Backend service geliştirmeleri  
- `feature/frontend` - Frontend geliştirmeleri
- `feature/ai-service` - AI service geliştirmeleri
- `feature/database-migrations` - Veritabanı migration'ları

## Servis Bazlı Branch Yapısı

### Auth Service (feature/auth-service)
- `auth_service/` klasörü
- Auth ile ilgili tüm değişiklikler
- JWT, kullanıcı yönetimi, roller

### Backend Service (feature/backend-service)
- `backend/` klasörü
- Drop, waitlist, claim işlemleri
- Admin CRUD işlemleri

### Frontend (feature/frontend)
- `frontend/` klasörü
- React uygulaması
- UI/UX geliştirmeleri

### AI Service (feature/ai-service)
- `ai_service/` klasörü
- Gemini entegrasyonu
- RAG sistemi

### Database Migrations (feature/database-migrations)
- `backend/alembic/` klasörü
- `init-db/` klasörü
- Veritabanı şema değişiklikleri

## Çalışma Akışı

1. İlgili servis branch'ine geç:
```bash
git checkout feature/auth-service
```

2. Değişiklikleri yap ve commit et:
```bash
git add auth_service/
git commit -m "feat(auth): Add default admin creation"
```

3. Pull Request aç ve main'e merge et

4. Main branch'te tüm servisler birleşir

## Önemli Notlar

- Her servis kendi branch'inde bağımsız geliştirilir
- Main branch'e merge edilmeden önce test edilmelidir
- Pull Request açılırken açıklama yazılmalıdır

