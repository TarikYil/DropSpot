#!/usr/bin/env python
"""
Test Runner Script - DropSpot Test Suite

Bu script tüm testleri çalıştırır ve raporlar oluşturur.

Kullanım:
    python run_tests.py              # Tüm testleri çalıştır
    python run_tests.py --unit       # Sadece unit testler
    python run_tests.py --integration # Sadece integration testler
    python run_tests.py --coverage   # Coverage raporu ile
    python run_tests.py --verbose    # Detaylı output
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Komutu çalıştır ve sonucu göster"""
    if description:
        print(f"\n{'='*70}")
        print(f"  {description}")
        print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="DropSpot Test Runner")
    parser.add_argument("--unit", action="store_true", help="Sadece unit testleri çalıştır")
    parser.add_argument("--integration", action="store_true", help="Sadece integration testleri çalıştır")
    parser.add_argument("--auth", action="store_true", help="Sadece auth service testleri")
    parser.add_argument("--backend", action="store_true", help="Sadece backend testleri")
    parser.add_argument("--coverage", action="store_true", help="Coverage raporu oluştur")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detaylı output")
    parser.add_argument("--failfast", "-x", action="store_true", help="İlk hatada dur")
    
    args = parser.parse_args()
    
    # Base pytest komutu (tests klasöründen çalıştığımız için)
    pytest_cmd = "pytest ."
    
    # Marker seçimi
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.auth:
        markers.append("auth")
    if args.backend:
        markers.append("backend")
    
    if markers:
        pytest_cmd += f" -m '{' and '.join(markers)}'"
    
    # Flags
    if args.verbose:
        pytest_cmd += " -vv"
    if args.failfast:
        pytest_cmd += " -x"
    if args.coverage:
        pytest_cmd += " --cov=auth_service --cov=backend --cov-report=html --cov-report=term-missing"
    
    # Test çalıştır
    description = "DROPSPOT TEST SUITE"
    if markers:
        description += f" [{', '.join(markers).upper()}]"
    
    exit_code = run_command(pytest_cmd, description)
    
    if args.coverage and exit_code == 0:
        print("\n" + "="*70)
        print("  Coverage raporu oluşturuldu: htmlcov/index.html")
        print("="*70)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

