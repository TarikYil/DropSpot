"""
Backend Models Unit Tests
"""
import pytest
from datetime import datetime, timedelta

import sys
from pathlib import Path

# Backend'i path'e ekle
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models import Drop, Claim, Waitlist, DropStatus, ClaimStatus

# Backend'i path'ten çıkar (auth ile karışmaması için)
sys.path.remove(str(backend_path))


@pytest.mark.unit
@pytest.mark.backend
class TestDropModel:
    """Drop model testleri"""
    
    def test_drop_creation(self, db_session_backend):
        """Drop oluşturma"""
        drop = Drop(
            title="Test Drop",
            description="Test description",
            total_quantity=100,
            latitude=41.0082,
            longitude=28.9784,
            created_by=1,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=24)
        )
        
        db_session_backend.add(drop)
        db_session_backend.commit()
        
        assert drop.id is not None
        assert drop.title == "Test Drop"
        assert drop.status == DropStatus.SCHEDULED
        assert drop.claimed_quantity == 0
        assert drop.remaining_quantity == 100
        assert drop.is_active is True
    
    def test_drop_remaining_quantity_calculation(self, db_session_backend):
        """Kalan miktar hesaplama"""
        drop = Drop(
            title="Test Drop",
            total_quantity=100,
            claimed_quantity=30,
            latitude=41.0082,
            longitude=28.9784,
            created_by=1,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        db_session_backend.add(drop)
        db_session_backend.commit()
        
        assert drop.remaining_quantity == 70


@pytest.mark.unit
@pytest.mark.backend
class TestClaimModel:
    """Claim model testleri"""
    
    def test_claim_creation(self, db_session_backend):
        """Claim oluşturma"""
        # Önce drop oluştur
        drop = Drop(
            title="Test Drop",
            total_quantity=100,
            latitude=41.0082,
            longitude=28.9784,
            created_by=1,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1)
        )
        db_session_backend.add(drop)
        db_session_backend.commit()
        
        # Claim oluştur
        claim = Claim(
            drop_id=drop.id,
            user_id=1,
            quantity=1,
            claim_latitude=41.0082,
            claim_longitude=28.9784
        )
        
        db_session_backend.add(claim)
        db_session_backend.commit()
        
        assert claim.id is not None
        assert claim.status == ClaimStatus.PENDING
        assert claim.is_verified is False
        assert claim.verification_code is not None


@pytest.mark.unit
@pytest.mark.backend
class TestWaitlistModel:
    """Waitlist model testleri"""
    
    def test_waitlist_creation(self, db_session_backend):
        """Waitlist oluşturma"""
        # Drop oluştur
        drop = Drop(
            title="Test Drop",
            total_quantity=100,
            latitude=41.0082,
            longitude=28.9784,
            created_by=1,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=24)
        )
        db_session_backend.add(drop)
        db_session_backend.commit()
        
        # Waitlist entry oluştur
        waitlist = Waitlist(
            drop_id=drop.id,
            user_id=1,
            priority_score=0.5
        )
        
        db_session_backend.add(waitlist)
        db_session_backend.commit()
        
        assert waitlist.id is not None
        assert waitlist.is_notified is False
        assert waitlist.priority_score == 0.5

