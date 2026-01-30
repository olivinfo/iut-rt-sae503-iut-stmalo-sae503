.PHONY: build down logs
.DEFAULT_GOAL := help

all:
	@echo "Tout les tests"
	@make build
	@make test

help:
	@echo ""
	@echo "📋 Cibles disponibles dans ce Makefile :"
	@echo ""
	@echo "---------------------------------------------------------------"
	@echo "| Cible               | Description                           | "
	@echo "---------------------------------------------------------------"
	@echo "| all                 | Exécute toutes les étapes principales |"
	@echo "| install             | Installe les dépendances utilisateur  |"
	@echo "| build               | Construit et lance les conteneurs     |"
	@echo "| test                | Lance tous les tests                  |"
	@echo "| test-unitaires      | Lance les tests unitaires             |"
	@echo "| test-fonctionnel    | Lance les tests fonctionnels          |"
	@echo "| down                | Arrête et supprime les conteneurs     |"
	@echo "| logs                | Affiche les logs des conteneurs       |"
	@echo "| lint                | Analyse la qualité du code            |"
	@echo "| help                | Affiche ce message d'aide             |"
	@echo "---------------------------------------------------------------"
	@echo ""

install:
	@echo "Installation des depandances utillisateur..."
	pip install --no-cache-dir -r user-requirements.txt

build:
	@echo "Construction et lancement des conteneurs Docker..."
	clear
	docker compose down
	docker compose up --build

# Nettoyer l'environnement
clean:
	@echo "Nettoyage de l'environnement..."
	$(DOCKER_COMPOSE) down --volumes --rmi all
	docker system prune -a -f
	@echo "Environnement nettoyé"

test:
	@echo "Tester tout les tests"
	- make lint
	- make test-unitaires
	- make test-fonctionnel

test-unitaires:
	@echo "Tester les codes python..."
	pytest citations_haddock/quotes/test.py
	pytest citations_haddock/search/test.py
	pytest citations_haddock/users/test.py

test-fonctionnel:
	@echo "Tester les fonctionnalitées de l'application..."
	pytest tests/test_functional.py


down:
	@echo "Arrêt et suppression des conteneurs Docker..."
	docker compose down

logs:
	@echo "Affichage des logs des conteneurs Docker..."
	docker compose logs -f

lint:
	@echo "Analyse du code python"
	pylint --rcfile=.pylintrc .
