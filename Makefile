.PHONY: build down logs

build:
	@echo "Construction et lancement des conteneurs Docker..."
	docker compose up --build

down:
	@echo "Arrêt et suppression des conteneurs Docker..."
	docker compose down

logs:
	@echo "Affichage des logs des conteneurs Docker..."
	docker compose logs -f
