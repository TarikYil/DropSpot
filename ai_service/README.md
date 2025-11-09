# DropSpot AI Service 🤖

Gemini tabanlı RAG (Retrieval Augmented Generation) chatbot servisi.

## 🎯 Özellikler

- **Gemini AI Integration**: Google Gemini Pro modeli ile güçlü AI yanıtları
- **RAG Sistemi**: Backend'den gerçek zamanlı veri çekerek context-aware yanıtlar
- **Chat History**: Konuşma geçmişi ile bağlamsal sohbet
- **Auth Integration**: Kullanıcıya özel bilgiler (token ile)
- **Platform Knowledge**: Drop'lar, waitlist, claim süreçleri hakkında bilgi

## 🏗️ Mimari

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  AI Service  │─────▶│   Gemini    │
└─────────────┘      │   (FastAPI)  │      │     API     │
                     └──────┬───────┘      └─────────────┘
                            │
                            ├─────▶ Backend Service (RAG Data)
                            │
                            └─────▶ Auth Service (User Info)
```

## 📁 Klasör Yapısı

```
ai_service/
├── main.py                 # FastAPI uygulaması
├── config.py              # Konfigürasyon
├── schemas.py             # Pydantic şemaları
├── routers/
│   └── chat.py           # Chat endpoints
├── services/
│   ├── gemini_service.py # Gemini API wrapper
│   └── rag_service.py    # RAG context builder
├── utils/
│   └── auth.py           # Auth utilities
├── requirements.txt       # Dependencies
└── Dockerfile            # Container image
```

## 🚀 Kullanım

### Docker ile Çalıştırma

```bash
# AI service'i başlat
docker-compose up -d ai_service

# Logları izle
docker-compose logs -f ai_service
```

### API Endpoints

#### 1. Soru Sor (Token İle)

```bash
# Login yap ve token al
TOKEN=$(curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' | jq -r '.access_token')

# AI'ya soru sor
curl -X POST "http://localhost:8004/api/chat/ask" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Aktif drop'\''lar neler?",
    "include_context": true
  }'
```

#### 2. Soru Sor (Token Olmadan)

```bash
curl -X POST "http://localhost:8004/api/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "DropSpot platformu nedir?",
    "include_context": true
  }'
```

#### 3. Chat History ile Sohbet

```bash
curl -X POST "http://localhost:8004/api/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Peki claim nasıl yapılır?",
    "chat_history": [
      {"role": "user", "content": "DropSpot nedir?"},
      {"role": "assistant", "content": "DropSpot sınırlı ürünlere erişim platformudur..."}
    ],
    "include_context": true
  }'
```

#### 4. Health Check

```bash
curl http://localhost:8004/health
```

## 📊 Response Örnekleri

### Başarılı Chat Response

```json
{
  "response": "DropSpot'ta aktif olan drop'lar:\n\n1. Test Drop: Test drop description (Stok: 95/100)\n2. Premium Tişört: Sınırlı sayıda premium tişört (Stok: 48/50)\n\nBu drop'lara katılmak için /api/waitlist/join endpoint'ini kullanabilirsiniz.",
  "context_used": true,
  "timestamp": "2024-11-07T14:30:00Z"
}
```

### Health Response

```json
{
  "status": "healthy",
  "service": "DropSpot AI Service",
  "version": "1.0.0",
  "gemini_status": "healthy",
  "backend_status": "healthy"
}
```

## 🔧 Konfigürasyon

Environment değişkenleri:

```env
# Server
PORT=8004

# Gemini API
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-pro

# Services
AUTH_SERVICE_URL=http://auth_service:8000
BACKEND_SERVICE_URL=http://backend:8002

# RAG Settings
MAX_CONTEXT_LENGTH=4000
MAX_CHAT_HISTORY=10
TEMPERATURE=0.7
TOP_P=0.95
TOP_K=40

# Security
SECRET_KEY=your-secret-key
```

## 💡 RAG Context Stratejisi

AI servisi soruları analiz ederek backend'den ilgili bilgileri çeker:

| Anahtar Kelimeler | Backend Endpoint | Context |
|-------------------|-----------------|---------|
| drop, ürün, aktif | `/api/drops/active` | Aktif drop listesi |
| waitlist, bekleme | - | Waitlist genel bilgi |
| claim, hak kazanma | - | Claim süreci açıklaması |
| admin, yönetim | - | Admin yetkiler |
| platform, nedir | - | Platform genel bilgi |

## 🤖 Gemini Model Ayarları

```python
generation_config = {
    "temperature": 0.7,      # Yaratıcılık seviyesi (0-1)
    "top_p": 0.95,           # Nucleus sampling
    "top_k": 40,             # Top-k sampling
    "max_output_tokens": 2048 # Max cevap uzunluğu
}
```

## 🔐 Güvenlik

- **Token Opsiyonel**: Token olmadan genel bilgi, token ile kişisel bilgi
- **Safety Settings**: Zararlı içerik filtreleme aktif
- **CORS**: Cross-origin isteklere izin verilir (production'da kısıtlanmalı)
- **Rate Limiting**: TODO: Implement rate limiting

## 📈 Performans

- **Gemini API Latency**: ~1-3 saniye
- **RAG Context Fetching**: ~100-500ms
- **Total Response Time**: ~1.5-4 saniye

## 🧪 Test Senaryoları

```bash
# 1. Platform hakkında genel soru
"DropSpot nedir?"

# 2. Aktif drop'lar
"Şu anda hangi drop'lar var?"

# 3. Waitlist işlemleri
"Bekleme listesine nasıl katılırım?"

# 4. Claim süreci
"Claim nasıl yapılır?"

# 5. Admin işlemleri
"Admin olarak ne yapabilirim?"

# 6. Kullanıcı özel (token ile)
"Benim claim'lerim neler?"
```

## 🚨 Hata Durumları

| Durum | Status Code | Açıklama |
|-------|-------------|----------|
| Gemini API hatası | 500 | API key geçersiz veya quota aşıldı |
| Backend ulaşılamaz | 500 | Backend servisi çalışmıyor |
| Geçersiz request | 422 | Message boş veya çok uzun |

## 📝 Geliştirme Notları

1. **Gemini API Key**: Google AI Studio'dan ücretsiz alınabilir
2. **Context Length**: 4000 karakter sınırı (daha fazlası için ayarlanabilir)
3. **Chat History**: Son 10 mesaj saklanır
4. **Async Operations**: Tüm API çağrıları async

## 🔮 Gelecek Özellikler

- [ ] Redis ile chat history cache
- [ ] Rate limiting
- [ ] Prompt engineering iyileştirmeleri
- [ ] Vector database entegrasyonu (semantic search)
- [ ] Multi-language support
- [ ] User feedback sistemi
- [ ] A/B testing farklı promptlar için

## 📚 Kaynaklar

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RAG Pattern](https://www.pinecone.io/learn/retrieval-augmented-generation/)

