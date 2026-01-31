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
	@echo "| install-trivy       | Installe trivy pour scanner les vuln  |"
	@echo "| build               | Construit et lance les conteneurs     |"
	@echo "| build-images        | Construit les images docker           |"
	@echo "| clean               | Nettoie l'environnement               |"
	@echo "| test                | Lance tous les tests                  |"
	@echo "| test-unitaires      | Lance les tests unitaires             |"
	@echo "| test-fonctionnel    | Lance les tests fonctionnels          |"
	@echo "| test-securiter      | Lance les tests de sécurité trivy     |"
	@echo "| down                | Arrête et supprime les conteneurs     |"
	@echo "| logs                | Affiche les logs des conteneurs       |"
	@echo "| lint                | Analyse la qualité du code            |"
	@echo "| help                | Affiche ce message d'aide             |"
	@echo "---------------------------------------------------------------"
	@echo ""

install:
	@echo "Installation des depandances utillisateur..."
	pip install --no-cache-dir -r user-requirements.txt

install-trivy:
	@echo "Installation de Trivy"
	sudo apt-get install wget gnupg
	wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
	echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
	sudo apt-get update
	sudo apt-get install trivy

build:
	@echo "Construction et lancement des conteneurs Docker..."
	clear
	docker compose down
	docker compose up --build

build-images:
	@echo "Construction des images pour les registy"
	docker build -t kitami1/sae503-quotes -f citations_haddock/quotes/Dockerfile citations_haddock
	docker build -t kitami1/sae503-search -f citations_haddock/search/Dockerfile citations_haddock
	docker build -t kitami1/sae503-users -f citations_haddock/users/Dockerfile citations_haddock


# Nettoyer l'environnement
clean:
	@echo "Nettoyage de l'environnement..."
	docker compose down --volumes --rmi all
	docker system prune -a -f
	@echo "Environnement nettoyé"

test:
	@echo "Tester tout les tests"
	- make lint
	- make test-unitaires
	- make test-fonctionnel

test-unitaires:
	@clear
	@echo "Tester les codes python..."
	pytest citations_haddock/quotes/test.py
	pytest citations_haddock/search/test.py
	pytest citations_haddock/users/test.py

test-fonctionnel:
	@clear
	@echo "Tester les fonctionnalitées de l'application..."
	pytest tests/test_functional.py

test-securiter:
	@clear
	@echo "Test de sécurité sur les Dockerfile"
 	trivy config --file-patterns "dockerfile:Dockerfile" citations_haddock/	# Dockerfiles
	trivy fs --scanners vuln --scanners misconfig,vuln .	# Config docker, kube, pip etc
	trivy image --scanners vuln,misconfig sae503-kc-md-quotes:latest	# Images
	trivy fs --scanners secret .										# Secrets

down:
	@echo "Arrêt et suppression des conteneurs Docker..."
	docker compose down

logs:
	@echo "Affichage des logs des conteneurs Docker..."
	docker compose logs -f

lint:
	@echo "Analyse du code python"
	pylint --rcfile=.pylintrc .
