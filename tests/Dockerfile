# Test Service Dockerfile
FROM python:3.11-slim

LABEL maintainer="DropSpot Team"
LABEL description="DropSpot Test Service - Unit & Integration Tests"

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Test dependencies'i kopyala ve yükle
COPY tests/requirements.txt /app/tests/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/tests/requirements.txt

# Tüm projeyi kopyala (testler için gerekli)
COPY . /app/

# Test çalıştırma için environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Test database URLs
ENV TEST_AUTH_DATABASE_URL=postgresql://postgres:postgres@postgres:5432/test_auth_db
ENV TEST_BACKEND_DATABASE_URL=postgresql://postgres:postgres@postgres:5432/test_dropspot_db

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pytest; print('Test service ready')" || exit 1

# Default command - tüm testleri çalıştır
CMD ["pytest", "tests/", "-v", "--tb=short"]

