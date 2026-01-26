.PHONY: build down logs

all:
	@echo "Tout les tests"
	make lint
	make test


install:
	@echo "Installation des depandances utillisateur..."
	pip install --no-cache-dir -r user-requirements.txt

build:
	@echo "Construction et lancement des conteneurs Docker..."
	docker compose up --build

test:
	@echo "Tester les codes python..."
	pytest citations_haddock/quotes/test.py
	pytest citations_haddock/search/test.py
	pytest citations_haddock/users/test.py
down:
	@echo "Arrêt et suppression des conteneurs Docker..."
	docker compose down

logs:
	@echo "Affichage des logs des conteneurs Docker..."
	docker compose logs -f

lint:
	@echo "Analyse du code python"
	pylint --rcfile=.pylintrc .




