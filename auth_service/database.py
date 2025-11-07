from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL bağlantı bilgileri
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/auth_db"
)

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# SessionLocal sınıfı - her bir veritabanı oturumu bu sınıfın bir instance'ı olacak
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base sınıfı - tüm modeller bu sınıftan türetilecek
Base = declarative_base()


# Dependency - her request için veritabanı oturumu oluşturur
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

