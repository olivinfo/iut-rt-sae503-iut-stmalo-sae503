# LOT 3 : Refactorisation de l'application

## 1. Introduction

### 1.1 Objectif
Refactoriser l'application monolithique en 3 microservices distincts selon les responsabilités fonctionnelles :
1. Service **Users** : Gestion des utilisateurs
2. Service **Quotes** : Gestion des citations
3. Service **Search** : Recherche de citations

### 1.2 Respect des 12-Factor App
La refactorisation respecte les principes des [12-Factor App](https://12factor.net/fr/).

## 2. Architecture de l'application refactorisée

### 2.1 Décomposition en microservices

```
Application monolithique (citations_haddock.py)
           |
           ├── Service Users (microservices/users/)
           |   ├── app.py
           |   ├── requirements.txt
           |   └── Dockerfile
           |
           ├── Service Quotes (microservices/quotes/)
           |   ├── app.py
           |   ├── requirements.txt
           |   └── Dockerfile
           |
           └── Service Search (microservices/search/)
               ├── app.py
               ├── requirements.txt
               └── Dockerfile
```

### 2.2 Répartition des endpoints

| Microservice | Endpoints | Méthodes |
|--------------|-----------|----------|
| **Users** | `/users` | GET, POST |
| **Quotes** | `/quotes` | GET, POST |
|           | `/quotes/<id>` | DELETE |
| **Search** | `/search` | GET |

## 3. Service Users

### 3.1 Responsabilités
- Gestion des utilisateurs (CRUD)
- Authentification (bonus)
- Initialisation depuis CSV

### 3.2 Structure du code

**Fichier** : `microservices/users/app.py`

Points clés :
- Endpoints : `GET /users`, `POST /users`
- Connexion à Redis via variables d'environnement
- Authentification via `ADMIN_KEY`
- Health check : `GET /health`
- Documentation Swagger : `/apidocs`

### 3.3 Configuration

Variables d'environnement :
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
APP_PORT=5000
ADMIN_KEY=<secret>
CSV_FILE_USERS=initial_data_users.csv
```

### 3.4 Dockerfile

Principe :
- Image de base : `python:3.11-slim` ou `python:3.11-alpine`
- Utilisateur non-root
- Multi-stage build si nécessaire
- Exposition du port 5000

Exemple :
```dockerfile
FROM python:3.11-slim

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY app.py .
COPY initial_data_users.csv .

# Changer de propriétaire
RUN chown -R appuser:appuser /app

# Utiliser l'utilisateur non-root
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
```

## 4. Service Quotes

### 4.1 Responsabilités
- Gestion des citations (CRUD)
- Initialisation depuis CSV
- Suppression par ID

### 4.2 Structure du code

**Fichier** : `microservices/quotes/app.py`

Points clés :
- Endpoints : `GET /quotes`, `POST /quotes`, `DELETE /quotes/<id>`
- Connexion à Redis via variables d'environnement
- Authentification via `ADMIN_KEY` pour POST/DELETE
- Health check : `GET /health`
- Documentation Swagger : `/apidocs`

### 4.3 Configuration

Variables d'environnement :
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
APP_PORT=5000
ADMIN_KEY=<secret>
CSV_FILE_QUOTES=initial_data_quotes.csv
```

### 4.4 Dockerfile

Structure similaire au service Users (voir 3.4).

## 5. Service Search

### 5.1 Responsabilités
- Recherche de citations par mot-clé
- Lecture seule dans Redis

### 5.2 Structure du code

**Fichier** : `microservices/search/app.py`

Points clés :
- Endpoint : `GET /search?keyword=<mot-clé>`
- Connexion à Redis via variables d'environnement
- Authentification via `ADMIN_KEY`
- Recherche insensible à la casse
- Health check : `GET /health`
- Documentation Swagger : `/apidocs`

### 5.3 Configuration

Variables d'environnement :
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
APP_PORT=5000
ADMIN_KEY=<secret>
```

### 5.4 Dockerfile

Structure similaire aux autres services (voir 3.4).

## 6. Bonnes pratiques appliquées

### 6.1 Principes 12-Factor

| Factor | Application |
|--------|-------------|
| **I. Codebase** | Un dépôt Git, plusieurs déploiements |
| **II. Dependencies** | `requirements.txt` explicite |
| **III. Config** | Variables d'environnement (pas de valeurs en dur) |
| **IV. Backing services** | Redis comme ressource attachée |
| **V. Build, release, run** | Séparation stricte (Docker build, K8s deploy) |
| **VI. Processes** | Services stateless, état dans Redis |
| **VII. Port binding** | Exposition sur port 5000 |
| **VIII. Concurrency** | Scaling horizontal via Kubernetes |
| **IX. Disposability** | Démarrage rapide, shutdown graceful |
| **X. Dev/prod parity** | Même conteneur partout |
| **XI. Logs** | Logs vers stdout/stderr |
| **XII. Admin processes** | Scripts séparés si nécessaire |

### 6.2 Sécurité

- **Pas de secrets dans le code** : Variables d'environnement uniquement
- **Utilisateur non-root** : USER dans Dockerfile
- **Images minimales** : slim ou alpine
- **Dépendances à jour** : Versions spécifiques dans requirements.txt
- **SecurityContext Kubernetes** : runAsNonRoot, readOnlyRootFilesystem

### 6.3 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Utilisation
logger.info("Service démarré")
logger.error("Erreur lors de la connexion à Redis")
```

### 6.4 Health checks

Chaque service expose un endpoint `/health` :

```python
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503
```

## 7. Fichiers de données initiales

### 7.1 Format CSV

**initial_data_users.csv** :
```csv
id,name,password
1,admin,admin123
2,user1,password1
3,user2,password2
```

**initial_data_quotes.csv** :
```csv
quote
Bachi-bouzouk!
Tonnerre de Brest!
Mille millions de mille sabords!
Moule à gaufres!
Ectoplasme!
```

### 7.2 Chargement initial

Le chargement des données CSV se fait au démarrage du service si Redis est vide :

```python
if not redis_client.exists("users"):
    if os.path.exists(CSV_FILE_USERS):
        # Charger les utilisateurs
```

## 8. Structure du repository Git

```
sae503-solaylilian/
├── microservices/
│   ├── users/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── initial_data_users.csv
│   ├── quotes/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── initial_data_quotes.csv
│   └── search/
│       ├── app.py
│       ├── requirements.txt
│       └── Dockerfile
├── docs/
│   └── LOT3-refactorisation.md
└── README.md
```

## 9. Build et test des images Docker

### 9.1 Build

```bash
# Service Users
cd microservices/users
docker build -t haddock-users:latest .

# Service Quotes
cd microservices/quotes
docker build -t haddock-quotes:latest .

# Service Search
cd microservices/search
docker build -t haddock-search:latest .
```

### 9.2 Test local avec Docker Compose

**docker-compose.yml** (pour tests locaux) :
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  users:
    build: ./microservices/users
    ports:
      - "5001:5000"
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
      ADMIN_KEY: test_key
    depends_on:
      - redis

  quotes:
    build: ./microservices/quotes
    ports:
      - "5002:5000"
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
      ADMIN_KEY: test_key
    depends_on:
      - redis

  search:
    build: ./microservices/search
    ports:
      - "5003:5000"
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
      ADMIN_KEY: test_key
    depends_on:
      - redis
```

Commandes :
```bash
# Démarrer
docker-compose up -d

# Tester
curl http://localhost:5001/health
curl http://localhost:5001/users -H "Authorization: test_key"

# Arrêter
docker-compose down
```

### 9.3 Scan de sécurité avec Trivy

```bash
# Scanner les images
trivy image haddock-users:latest
trivy image haddock-quotes:latest
trivy image haddock-search:latest

# Vérifier l'absence de vulnérabilités critiques
trivy image --severity HIGH,CRITICAL haddock-users:latest
```

## 10. Bonus : Authentification basée sur les utilisateurs

### 10.1 Principe

Au lieu d'utiliser une clé `ADMIN_KEY` statique, utiliser les identifiants/mots de passe stockés dans Redis.

### 10.2 Implémentation

```python
from functools import wraps
from flask import request, jsonify
import base64

def require_user_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        try:
            # Format: "Basic base64(username:password)"
            auth_type, credentials = auth_header.split(" ")
            if auth_type.lower() != "basic":
                return jsonify({"error": "Invalid auth type"}), 401

            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(":")

            # Vérifier dans Redis
            users_ids = redis_client.smembers("users")
            for user_key in users_ids:
                user = redis_client.hgetall(user_key)
                if user.get("name") == username and user.get("password") == password:
                    return f(*args, **kwargs)

            return jsonify({"error": "Invalid credentials"}), 401
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 401

    return decorated

# Utilisation
@app.route('/users', methods=['POST'])
@require_user_auth
def add_user():
    # ...
```

## 11. Checklist de refactorisation

- [ ] Service Users créé et fonctionnel
- [ ] Service Quotes créé et fonctionnel
- [ ] Service Search créé et fonctionnel
- [ ] Dockerfile pour chaque service
- [ ] Images Docker non-root
- [ ] Variables d'environnement pour la configuration
- [ ] Health checks implémentés
- [ ] Logs vers stdout/stderr
- [ ] CSV de données initiales
- [ ] Documentation Swagger fonctionnelle
- [ ] Tests locaux avec Docker Compose
- [ ] Scan Trivy sans vulnérabilités critiques
- [ ] Code versé dans Git
- [ ] Bonus authentification (optionnel)

## Annexes

### Annexe A : requirements.txt

```txt
Flask==3.0.0
redis==5.0.1
flasgger==0.9.7.1
```

### Annexe B : Commandes de test

```bash
# Test du service Users
curl -X GET http://localhost:5001/users \
  -H "Authorization: test_key"

curl -X POST http://localhost:5001/users \
  -H "Authorization: test_key" \
  -H "Content-Type: application/json" \
  -d '{"id": "10", "name": "Tintin", "password": "milou"}'

# Test du service Quotes
curl -X GET http://localhost:5002/quotes

curl -X POST http://localhost:5002/quotes \
  -H "Authorization: test_key" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1", "quote": "Sapajou!"}'

# Test du service Search
curl -X GET "http://localhost:5003/search?keyword=tonnerre" \
  -H "Authorization: test_key"
```
