"""
Auth Utils Unit Tests - Token ve şifre işlemleri
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt

# Test edilecek modül
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "auth_service"))

from utils.auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_password_strength,
    SECRET_KEY,
    ALGORITHM
)


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Şifre hash işlemleri testleri"""
    
    def test_password_hashing(self):
        """Şifre hash ve verify işlemi"""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    def test_password_uniqueness(self):
        """Aynı şifrenin her seferinde farklı hash üretmesi"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordValidation:
    """Şifre güçlülük validasyonu testleri"""
    
    def test_valid_password(self):
        """Geçerli şifre"""
        assert validate_password_strength("TestPass123") is True
    
    def test_too_short_password(self):
        """Çok kısa şifre"""
        with pytest.raises(Exception) as exc_info:
            validate_password_strength("Test1")
        assert "en az 8 karakter" in str(exc_info.value.detail)
    
    def test_no_uppercase_password(self):
        """Büyük harf içermeyen şifre"""
        with pytest.raises(Exception) as exc_info:
            validate_password_strength("testpass123")
        assert "büyük harf" in str(exc_info.value.detail)
    
    def test_no_lowercase_password(self):
        """Küçük harf içermeyen şifre"""
        with pytest.raises(Exception) as exc_info:
            validate_password_strength("TESTPASS123")
        assert "küçük harf" in str(exc_info.value.detail)
    
    def test_no_digit_password(self):
        """Rakam içermeyen şifre"""
        with pytest.raises(Exception) as exc_info:
            validate_password_strength("TestPassword")
        assert "rakam" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.auth
class TestTokenOperations:
    """JWT token işlemleri testleri"""
    
    def test_create_access_token(self):
        """Access token oluşturma"""
        data = {"sub": "1", "username": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50
        
        # Token decode edilebilmeli
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "1"
        assert decoded["username"] == "testuser"
        assert decoded["type"] == "access"
        assert "exp" in decoded
    
    def test_create_refresh_token(self):
        """Refresh token oluşturma"""
        data = {"sub": "1"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "1"
        assert decoded["type"] == "refresh"
    
    def test_decode_valid_token(self):
        """Geçerli token decode"""
        data = {"sub": "1", "username": "testuser"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        assert decoded["sub"] == "1"
        assert decoded["username"] == "testuser"
        assert decoded["type"] == "access"
    
    def test_decode_expired_token(self):
        """Süresi dolmuş token"""
        # Geçmişte expire olan token oluştur
        data = {"sub": "1"}
        expires = datetime.utcnow() - timedelta(minutes=30)
        
        token_data = data.copy()
        token_data.update({"exp": expires, "type": "access"})
        expired_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(Exception) as exc_info:
            decode_token(expired_token)
        assert exc_info.value.status_code == 401
    
    def test_decode_invalid_token(self):
        """Geçersiz token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception) as exc_info:
            decode_token(invalid_token)
        assert exc_info.value.status_code == 401
    
    def test_token_with_custom_expiration(self):
        """Özel expiration süresi ile token"""
        data = {"sub": "1"}
        custom_expire = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_expire)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        
        # Yaklaşık 2 saat sonra expire olmalı
        time_diff = (exp_time - now).total_seconds()
        assert 7000 < time_diff < 7300  # ~2 hours

