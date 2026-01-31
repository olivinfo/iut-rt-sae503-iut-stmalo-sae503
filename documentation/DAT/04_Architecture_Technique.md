# 3. Architecture Technique

## 3.1 Orchestrateur de conteneurs

### 3.1.1 Kubernetes

**Description** : Kubernetes est utilisé comme orchestrateur de conteneurs pour gérer le déploiement, la mise à l'échelle et l'exploitation des applications conteneurisées.

**Configuration actuelle** :

- **Namespace** : `haddock` - Isolement logique de tous les services
- **Pods** : Conteneurs exécutant les microservices et Redis
- **Services** : Exposition des microservices via des services Kubernetes
- **Ingress** : Configuration de Traefik pour le routage des requêtes HTTP
- **Deployments** : Gestion des répliques et des mises à jour

**Fichiers de configuration** :

```yaml
# Exemple de configuration de namespace
apiVersion: v1
kind: Namespace
metadata:
  name: haddock
```

```yaml
# Exemple de deployment pour le service quotes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quotes-service
  namespace: haddock
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quotes-service
  template:
    metadata:
      labels:
        app: quotes-service
    spec:
      containers:
      - name: quotes-service
        image: kitami1/sae503-quotes:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
```

### 3.1.2 Configuration réseau

**Réseau Kubernetes** :
- **Type** : Network overlay (par défaut avec Kubernetes)
- **Nom** : `proxy` - Réseau dédié pour l'isolation des services
- **Communication** : Tous les pods peuvent communiquer entre eux dans le même namespace

**Configuration Traefik** :
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: reverse-proxy
  namespace: haddock
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  rules:
  - host: localhost.local
    http:
      paths:
      - path: /users
        pathType: Prefix
        backend:
          service:
            name: backend-users
            port:
              number: 80
      - path: /quotes
        pathType: Prefix
        backend:
          service:
            name: backend-quotes
            port:
              number: 80
```

## 3.2 Microservices

### 3.2.1 Users Service

**Fonctionnalités** :
- Gestion complète des utilisateurs (CRUD)
- Authentification et autorisation
- Stockage des informations utilisateurs

**Technologies** :
- **Langage** : Python 3.12
- **Framework** : Flask
- **Base de données** : Redis
- **Documentation** : Flasgger (Swagger)

**Endpoints** :
- `GET /users` - Liste tous les utilisateurs
- `POST /users` - Crée un nouvel utilisateur
- `GET /users/{id}` - Récupère un utilisateur spécifique
- `PUT /users/{id}` - Met à jour un utilisateur
- `DELETE /users/{id}` - Supprime un utilisateur

**Exemple de code** :
```python
@app.route('/users', methods=['GET'])
def get_users():
    """
    Récupérer tous les utilisateurs
    ---
    responses:
      200:
        description: Liste des utilisateurs
    """
    users = redis_client.smembers("users")
    user_list = []
    for user in users:
        user_list.append(redis_client.hgetall(user))
    return jsonify(user_list), 200
```

### 3.2.2 Quotes Service

**Fonctionnalités** :
- Gestion des citations
- Ajout et suppression de citations
- Récupération de toutes les citations
- Authentification requise pour les opérations de modification

**Technologies** :
- **Langage** : Python 3.12
- **Framework** : Flask
- **Base de données** : Redis
- **Documentation** : Flasgger (Swagger)

**Endpoints** :
- `GET /quotes` - Liste toutes les citations
- `POST /quotes` - Ajoute une nouvelle citation (authentification requise)
- `DELETE /quotes/{id}` - Supprime une citation (authentification requise)
- `GET /quotes/health` - Vérification de santé

**Mécanisme d'authentification** :
```python
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get("Authorization")
        if not auth_key:
            return jsonify({"error": "Authorization header is missing"}), 401
        token_key = f"token:{auth_key}"
        if not redis_client.exists(token_key):
            return jsonify({"error": "Unauthorized: Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated
```

### 3.2.3 Search Service

**Fonctionnalités** :
- Recherche de citations par mots-clés
- Filtrage et tri des résultats
- Optimisation des performances de recherche

**Technologies** :
- **Langage** : Python 3.12
- **Framework** : Flask
- **Base de données** : Redis
- **Documentation** : Flasgger (Swagger)

**Endpoints** :
- `GET /search` - Recherche de citations
- `GET /search?query={terme}` - Recherche avec terme spécifique
- `GET /search?user={id}` - Recherche par utilisateur

**Exemple de recherche** :
```python
@app.route('/search', methods=['GET'])
def search_quotes():
    query = request.args.get('query', '')
    if query:
        # Recherche dans Redis
        results = []
        for quote_id in redis_client.smembers("quotes"):
            quote_data = redis_client.hgetall(quote_id)
            if query.lower() in quote_data.get('quote', '').lower():
                results.append(quote_data)
        return jsonify(results), 200
    return jsonify([]), 200
```

## 3.3 Stockage des données

### 3.3.1 Redis

**Choix technique** : Redis a été choisi pour sa simplicité, ses performances et sa compatibilité avec les besoins du projet.

**Configuration** :
- **Version** : Redis 8
- **Port** : 6379
- **Base de données** : DB 0 (par défaut)
- **Persistance** : Configuration par défaut (RDB)

**Structure des données** :

```
# Utilisateurs
users: {user_id1, user_id2, ...}
user:{id}:
  - id: "1"
  - name: "Alice"
  - password: "hashed_password"

# Citations
quotes: {quote_id1, quote_id2, ...}
quotes:{id}:
  - id: "1"
  - user_id: "1"
  - quote: "Citation exemple"

# Tokens d'authentification
token:{auth_key}:
  - user_id: "1"
  - expires: "timestamp"
```

**Exemple de déploiement Redis** :
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-deployment
  namespace: haddock
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:8
        ports:
        - containerPort: 6379
```

### 3.3.2 Persistance des données

**Configuration actuelle** :
- Les données sont stockées dans le pod Redis
- Pas de configuration explicite de PersistentVolumeClaim

**Améliorations prévues** :
- Configuration de PersistentVolumeClaims pour Redis
- Mise en place de sauvegardes régulières
- Configuration de stratégies de rétention

## 3.4 Réseau et reverse proxy

### 3.4.1 Traefik

**Fonctionnalités** :
- Reverse proxy et load balancer
- Routage dynamique des requêtes
- Terminaison SSL
- Dashboard de monitoring
- Rate limiting (configurable)

**Configuration Docker Compose** :
```yaml
services:
  traefik:
    image: "traefik"
    container_name: "traefik"
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    networks:
      - proxy
    command:
      - "--providers.docker=true"
      - "--api.insecure=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=proxy"
      - "--entryPoints.web.address=:80"
      - "--entryPoints.haddock.address=:5000"
    ports:
      - "80:80"
      - "5000:5000"
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
```

### 3.4.2 Configuration réseau

**Réseau Docker** :
```yaml
networks:
  proxy:
    name: proxy
```

**Fonctionnement** :
1. Tous les services sont connectés au réseau `proxy`
2. Traefik découvre automatiquement les services via Docker
3. Les requêtes sont routées en fonction des labels Docker
4. Le trafic est isolé dans le réseau Kubernetes

### 3.4.3 Labels Traefik

Exemple de configuration pour le service quotes :
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.quotes.rule=PathPrefix(`/quotes`)"
  - "traefik.http.routers.quotes.entrypoints=haddock"
  - "traefik.http.services.quotes.loadbalancer.server.port=5000"
```

## 3.5 Sécurité

### 3.5.1 Mesures de sécurité implémentées

1. **Authentification** :
   - Système de tokens basé sur Redis
   - Vérification des tokens pour les endpoints sensibles
   - Décorateur `@require_auth` pour la protection

2. **Images Docker sécurisées** :
   - Utilisation d'images minimales (`python:3.12-slim`)
   - Exécution avec utilisateurs non-root
   - Suppression des privilèges root

3. **Configuration Traefik** :
   - Options de sécurité Docker (`no-new-privileges:true`)
   - Isolation réseau
   - Possibilité de rate limiting

4. **Kubernetes** :
   - Isolation via namespace
   - Gestion des secrets
   - Configuration de securityContext

### 3.5.2 Exemple de Dockerfile sécurisé

```dockerfile
FROM python:3.12-slim
LABEL org.opencontainers.image.source=https://github.com/olivinfo/sae503-kc-md
WORKDIR /app

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y curl --no-install-recommends

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser user
USER user

COPY quotes/ .
COPY data/ .

ENV REDIS_HOST="backend-redis"

EXPOSE 5000

HEALTHCHECK --interval=5s --timeout=2s --retries=2 --start-period=5s CMD curl --fail http://localhost:5000/quotes/health || exit 1

CMD ["python", "quotes.py"]
```

### 3.5.3 Configuration de sécurité Kubernetes

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
```

### 3.5.4 Améliorations de sécurité prévues

1. **Secrets** : Externalisation complète dans Kubernetes Secrets
2. **Rate Limiting** : Activation et configuration dans Traefik
3. **Network Policies** : Restriction du trafic entre pods
4. **Authentification** : Migration vers JWT ou OAuth2
5. **Monitoring** : Configuration de logs et alertes de sécurité

Voir le fichier [SECURITY.md](../../../SECURITY.md) pour une analyse complète de la sécurité.