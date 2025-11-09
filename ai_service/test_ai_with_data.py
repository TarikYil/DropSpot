"""
AI Servisini test etmek için script
Sentetik verilerle AI servisini test eder
"""
import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Container içinden erişim için
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8004")
BACKEND_URL = os.getenv("BACKEND_SERVICE_URL", "http://backend:8002")

# Test sonuçları dizini
RESULTS_DIR = Path("/app/test_results")
RESULTS_DIR.mkdir(exist_ok=True)


def test_ai_service():
    """AI servisini test et"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"test_results_{timestamp}.txt"
    json_file = RESULTS_DIR / f"test_results_{timestamp}.json"
    
    print("=" * 60)
    print("AI SERVİSİ TEST - VERİTABANINDAN VERİLER")
    print("=" * 60)
    print(f"\nTest sonuçları kaydedilecek: {results_file}")
    print(f"JSON sonuçları kaydedilecek: {json_file}\n")
    
    # Test sonuçları
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "backend_url": BACKEND_URL,
        "ai_service_url": AI_SERVICE_URL,
        "tests": []
    }
    
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("AI SERVİSİ TEST - VERİTABANINDAN VERİLER")
    output_lines.append("=" * 60)
    output_lines.append(f"Test Zamanı: {test_results['timestamp']}\n")
    
    # Backend'den drop sayısını kontrol et
    output_lines.append("\n1. Backend Drop Kontrolü:")
    try:
        response = requests.get(f"{BACKEND_URL}/api/drops/?limit=10")
        if response.status_code == 200:
            drops = response.json()
            drop_count = len(drops)
            output_lines.append(f"   ✓ Backend'de {drop_count} adet drop bulundu")
            test_results["backend_drop_count"] = drop_count
        else:
            output_lines.append(f"   ✗ Backend'e erişilemedi: {response.status_code}")
            test_results["backend_status"] = "error"
            test_results["backend_error"] = f"Status {response.status_code}"
            return
    except Exception as e:
        output_lines.append(f"   ✗ Hata: {e}")
        test_results["backend_status"] = "error"
        test_results["backend_error"] = str(e)
        return
    
    # Test soruları
    test_questions = [
        {
            "name": "Drop Listesi",
            "message": "Tüm drop'ları listele ve detaylarını göster"
        },
        {
            "name": "Aktif Drop'lar",
            "message": "Şu anda aktif olan drop'lar neler?"
        },
        {
            "name": "Waitlist İstatistikleri",
            "message": "Waitlist istatistiklerini göster, kaç kişi bekliyor?"
        },
        {
            "name": "Stok Durumu",
            "message": "Hangi drop'larda stok kalmış?"
        }
    ]
    
    output_lines.append("\n2. AI Servisi Testleri:")
    output_lines.append("-" * 60)
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test in enumerate(test_questions, 1):
        output_lines.append(f"\n{i}. {test['name']}:")
        output_lines.append(f"   Soru: {test['message']}")
        
        test_result = {
            "test_number": i,
            "name": test['name'],
            "question": test['message'],
            "status": "unknown",
            "context_used": False,
            "response": "",
            "error": None
        }
        
        try:
            payload = {
                "message": test['message'],
                "include_context": True
            }
            
            response = requests.post(
                f"{AI_SERVICE_URL}/api/chat/ask",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '')
                context_used = data.get('context_used', False)
                
                test_result["status"] = "passed"
                test_result["context_used"] = context_used
                test_result["response"] = answer
                test_result["response_length"] = len(answer)
                
                output_lines.append(f"   ✓ Cevap alındı (Context: {'✓' if context_used else '✗'})")
                output_lines.append(f"   Cevap Uzunluğu: {len(answer)} karakter")
                output_lines.append(f"   Cevap (ilk 500 karakter):")
                output_lines.append(f"   {answer[:500]}...")
                
                passed_tests += 1
            else:
                test_result["status"] = "failed"
                test_result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                output_lines.append(f"   ✗ Hata: {response.status_code}")
                output_lines.append(f"   {response.text[:200]}")
                failed_tests += 1
                
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
            output_lines.append(f"   ✗ Hata: {e}")
            failed_tests += 1
        
        test_results["tests"].append(test_result)
    
    # Özet
    output_lines.append("\n" + "=" * 60)
    output_lines.append("TEST ÖZETİ:")
    output_lines.append(f"  Toplam Test: {len(test_questions)}")
    output_lines.append(f"  Başarılı: {passed_tests}")
    output_lines.append(f"  Başarısız: {failed_tests}")
    output_lines.append(f"  Başarı Oranı: {(passed_tests/len(test_questions)*100):.1f}%")
    output_lines.append("=" * 60)
    output_lines.append("TEST TAMAMLANDI!")
    output_lines.append("=" * 60)
    
    test_results["summary"] = {
        "total_tests": len(test_questions),
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": (passed_tests/len(test_questions)*100) if test_questions else 0
    }
    
    # Ekrana yazdır
    for line in output_lines:
        print(line)
    
    # Dosyaya kaydet
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"\n✓ Test sonuçları kaydedildi: {results_file}")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON sonuçları kaydedildi: {json_file}")
    except Exception as e:
        print(f"\n⚠ Sonuçlar kaydedilemedi: {e}")


if __name__ == "__main__":
    test_ai_service()

