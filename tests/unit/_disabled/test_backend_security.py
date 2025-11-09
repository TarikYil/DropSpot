"""
Backend Security Utils Unit Tests
"""
import pytest
from unittest.mock import Mock, patch
from jose import jwt

import sys
from pathlib import Path

# Backend'i path'e ekle
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from utils.security import decode_token, calculate_distance, SECRET_KEY, ALGORITHM

# Backend'i path'ten çıkar
sys.path.remove(str(backend_path))


@pytest.mark.unit
@pytest.mark.backend
class TestTokenDecode:
    """Token decode testleri"""
    
    def test_decode_valid_token(self):
        """Geçerli token decode"""
        payload = {"sub": "1", "username": "testuser", "type": "access"}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        decoded = decode_token(token)
        assert decoded["sub"] == "1"
        assert decoded["username"] == "testuser"
    
    def test_decode_invalid_token(self):
        """Geçersiz token"""
        with pytest.raises(Exception) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401


@pytest.mark.unit
@pytest.mark.backend
class TestDistanceCalculation:
    """Mesafe hesaplama testleri"""
    
    def test_same_location(self):
        """Aynı konum - mesafe 0 olmalı"""
        lat, lon = 41.0082, 28.9784
        distance = calculate_distance(lat, lon, lat, lon)
        assert distance == 0.0
    
    def test_known_distance(self):
        """Bilinen mesafe - İstanbul Taksim to Kadıköy yaklaşık 8-9 km"""
        # Taksim
        lat1, lon1 = 41.0369, 28.9850
        # Kadıköy
        lat2, lon2 = 40.9883, 29.0253
        
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        
        # Yaklaşık 8-9 km olmalı
        assert 7000 < distance < 10000
    
    def test_distance_symmetry(self):
        """Mesafe hesabı simetrik olmalı"""
        lat1, lon1 = 41.0082, 28.9784
        lat2, lon2 = 40.9883, 29.0253
        
        distance1 = calculate_distance(lat1, lon1, lat2, lon2)
        distance2 = calculate_distance(lat2, lon2, lat1, lon1)
        
        assert distance1 == distance2
    
    def test_hemisphere_distance(self):
        """Yarımküre arası mesafe"""
        # İstanbul
        lat1, lon1 = 41.0082, 28.9784
        # Sydney
        lat2, lon2 = -33.8688, 151.2093
        
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        
        # Çok uzak olmalı (13000+ km)
        assert distance > 13000000  # 13000 km

