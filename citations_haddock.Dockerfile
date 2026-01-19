# Utilisation d'une image Python officielle
FROM python:3.11-slim

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY citations_haddock/requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY ./data/ .

COPY ./citations_haddock/ .

# Définition des variables d'environnement
ENV REDIS_HOST=redis \
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    APP_PORT=5000 \
    ADMIN_KEY=default_key \
    CSV_FILE_USERS=initial_data_users.csv \
    CSV_FILE_QUOTES=initial_data_quotes.csv

# Exposition du port de l'application
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "citations_haddock.py"]
