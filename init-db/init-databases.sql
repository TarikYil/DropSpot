-- Auth servisi için database (zaten POSTGRES_DB ile oluşturulacak)
-- Bu dosya postgres container'ı ilk başlatıldığında çalışır

-- Backend servisi için ikinci database oluştur
SELECT 'CREATE DATABASE dropspot_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dropspot_db')\gexec

