"""
DropSpot Test Suite

Bu modül auth_service ve backend servislerinin unit ve integration testlerini içerir.

Test Tipleri:
- unit: Hızlı, izole birim testleri
- integration: Daha yavaş, servisler arası entegrasyon testleri

Kullanım:
    # Tüm testleri çalıştır
    pytest tests/
    
    # Sadece unit testleri
    pytest tests/ -m unit
    
    # Sadece integration testleri  
    pytest tests/ -m integration
    
    # Coverage ile
    pytest tests/ --cov=auth_service --cov=backend --cov-report=html
"""

__version__ = "1.0.0"

