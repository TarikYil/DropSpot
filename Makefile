.PHONY: help build up down restart logs clean test

help: ## Yardım menüsünü gösterir
	@echo "DropSpot - Auth Service Komutları:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Docker imajlarını oluşturur
	docker-compose build

up: ## Servisleri başlatır
	docker-compose up -d
	@echo "✅ Servisler başlatıldı!"
	@echo "📚 API Dokümantasyonu: http://localhost:8000/docs"
	@echo "🗄️  pgAdmin: http://localhost:5050 (admin@dropspot.com / admin)"

down: ## Servisleri durdurur
	docker-compose down
	@echo "✅ Servisler durduruldu!"

restart: ## Servisleri yeniden başlatır
	docker-compose restart
	@echo "✅ Servisler yeniden başlatıldı!"

logs: ## Tüm servislerin loglarını gösterir
	docker-compose logs -f

logs-auth: ## Auth servisinin loglarını gösterir
	docker-compose logs -f auth_service

logs-db: ## PostgreSQL loglarını gösterir
	docker-compose logs -f postgres

ps: ## Çalışan servisleri listeler
	docker-compose ps

clean: ## Servisleri durdurur ve volume'leri siler (DİKKAT: Tüm veriler silinir!)
	docker-compose down -v
	@echo "⚠️  Tüm veriler silindi!"

shell-auth: ## Auth servisine shell açar
	docker-compose exec auth_service /bin/bash

shell-db: ## PostgreSQL'e bağlanır
	docker-compose exec postgres psql -U postgres -d auth_db

migrate: ## Database migration çalıştırır (gelecekte eklenecek)
	@echo "⚠️  Migration sistemi henüz eklenmedi (Alembic)"

test: ## Testleri çalıştırır (gelecekte eklenecek)
	@echo "⚠️  Test sistemi henüz eklenmedi (Pytest)"

init: ## İlk kurulum (environment dosyası oluşturur ve servisleri başlatır)
	@if [ ! -f auth_service/.env ]; then \
		cp auth_service/.env.example auth_service/.env; \
		echo "✅ .env dosyası oluşturuldu"; \
	else \
		echo "⚠️  .env dosyası zaten mevcut"; \
	fi
	@make build
	@make up
	@echo ""
	@echo "🎉 Kurulum tamamlandı!"
	@echo "📚 API Dokümantasyonu: http://localhost:8000/docs"

