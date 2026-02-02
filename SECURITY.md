# SECURITY.md - SAE 5.03

Ce document décrit les mesures de sécurité mises en place dans le projet SAE 5.03, ainsi que les bonnes pratiques et les limitations actuelles.

## 1. Sécurité des secrets

**Exigence** : Toute information sensible (mots de passe, clés API, jetons) doit être stockée dans des **Secrets Kubernetes** et non en clair dans les fichiers de configuration ou le code.

**Implémentation actuelle** :

- Les clés d'authentification sont actuellement définies dans les variables d'environnement des déploiements Kubernetes
- Les Dockerfiles utilisent des images minimales et sécurisées
- Le Makefile inclut des commandes pour scanner les secrets avec Trivy

**Preuves** :

- Fichiers de déploiement Kubernetes utilisant des références à des secrets (ex: `envFrom: secretRef`).
- Commande `kubectl get secrets` montrant les secrets créés.
- Exemple de secret :

  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: app-secrets
  type: Opaque
  data:
    ADMIN_KEY: <base64_encoded_value>
  ```

**Améliorations possibles** :

- Externaliser complètement les secrets dans des gestionnaires de secrets comme HashiCorp Vault
- Utiliser des secrets Kubernetes pour toutes les informations sensibles
- Implémenter la rotation automatique des secrets

---

## 2. Isolation logique des environnements

**Exigence** : Les plateformes (qualification, production) doivent être isolées dans des **namespaces Kubernetes** distincts.

**Implémentation actuelle** :

- Le namespace `haddock` est utilisé pour isoler tous les services
- Les déploiements Kubernetes spécifient explicitement le namespace

**Preuves** :

- Commande `kubectl get namespaces` montrant les namespaces `qualification` et `production`.
- Manifestes de déploiement spécifiant le namespace :

  ```yaml
  metadata:
    namespace: haddock
  ```

**Améliorations possibles** :

- Créer des namespaces séparés pour différents environnements (dev, staging, prod)
- Implémenter des politiques de réseau (NetworkPolicies) pour isoler les namespaces
- Utiliser des quotas de ressources par namespace

---

## 3. Images Docker minimales et sécurisées

**Exigence** : Utilisation d’images Docker **minimales** (ex: `alpine`, `distroless`) et suppression des privilèges root.

**Implémentation actuelle** :

- Utilisation de `python:3.12-slim` comme image de base
- Création d'un utilisateur non-root dans les Dockerfiles
- Exécution des applications avec l'utilisateur non-root
- Suppression des privilèges root avec `USER user`

**Preuves** :

- Dockerfiles utilisant `FROM python:3.12-slim`
- Configuration du `securityContext` dans les manifestes Kubernetes :

  ```yaml
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  ```

**Exemple de Dockerfile sécurisé** :

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

**Améliorations possibles** :

- Utiliser des images encore plus minimales comme `python:3.12-alpine`
- Implémenter des scans de vulnérabilités automatiques dans le pipeline CI/CD
- Utiliser des images distroless pour les environnements de production

---

## 4. Gestion des tags d’images

**Exigence** : Éviter les tags flottants (`latest`), privilégier les tags immutables (ex: `v1.0.0`).

**Implémentation actuelle** :

- Les images Docker sont taguées avec des versions spécifiques (ex: `kitami1/sae503-quotes:1.0.0`)
- Les déploiements Kubernetes référencent des images avec des tags fixes

**Preuves** :

- Manifestes Kubernetes référençant des images avec des tags fixes :

  ```yaml
  image: kitami1/sae503-quotes:1.0.0
  ```

**Améliorations possibles** :

- Implémenter un système de versionnage sémantique
- Utiliser des tags basés sur les commits Git pour une traçabilité complète
- Mettre en place un registry d'images privé avec gestion des versions

---

## 5. Analyse de vulnérabilités avec Trivy

**Exigence** : Utilisation de **Trivy** pour scanner les images Docker et les manifestes Kubernetes.

**Implémentation actuelle** :

- Trivy est intégré dans le Makefile pour les scans de sécurité
- Les commandes Trivy sont disponibles pour scanner les Dockerfiles, les images et les secrets
- Installation automatisée de Trivy via le Makefile

**Preuves** :

- Rapport de scan Trivy (ex: `trivy image monregistry/monapp:1.0.0 > trivy-report.txt`).
- Intégration de Trivy dans un pipeline CI/CD (si applicable).

**Commandes Trivy disponibles** :

```bash
# Scanner les Dockerfiles
trivy config --file-patterns "dockerfile:Dockerfile" citations_haddock/

# Scanner les vulnérabilités et les mauvaises configurations
trivy fs --scanners vuln --scanners misconfig,vuln .

# Scanner les images Docker
trivy image --scanners vuln,misconfig sae503-kc-md-quotes:latest

# Scanner les secrets
trivy fs --scanners secret .
```

**Améliorations possibles** :

- Intégrer Trivy dans un pipeline CI/CD automatisé
- Configurer des seuils de vulnérabilités critiques pour bloquer les déploiements
- Générer des rapports de sécurité automatiques
- Mettre en place des scans réguliers des images en production

---

## 6. Limitation des requêtes HTTP

**Exigence** : Configuration d’un **limiteur de requêtes** (10 requêtes/minute) via Traefik.

**Implémentation actuelle** :

- Traefik est configuré comme reverse proxy avec des options de sécurité
- La configuration inclut des options de sécurité Docker (`no-new-privileges:true`)
- Le rate limiting est commenté dans la configuration mais peut être activé

**Preuves** :

- Configuration Traefik avec middleware de rate limiting :

  ```yaml
  apiVersion: traefik.containo.us/v1alpha1
  kind: Middleware
  metadata:
    name: ratelimit
  spec:
    rateLimit:
      average: 10
      burst: 10
  ```

**Configuration Traefik actuelle** :

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
```

**Améliorations possibles** :

- Activer et configurer le rate limiting dans Traefik
- Implémenter différentes limites pour différents endpoints
- Configurer des limites basées sur l'IP client
- Ajouter des mécanismes de protection contre les attaques DDoS

---

## 7. Persistance des données

**Exigence** : Utilisation de **volumes persistants** pour la base de données.

**Implémentation actuelle** :

- Redis est déployé comme service Kubernetes
- Les données sont persistées dans le pod Redis
- Pas de configuration explicite de PersistentVolumeClaim dans les manifests actuels

**Preuves** :

- Manifestes Kubernetes avec `PersistentVolumeClaim` :

  ```yaml
  volumes:
    - name: db-storage
      persistentVolumeClaim:
        claimName: db-pvc
  ```

**Améliorations possibles** :

- Configurer des PersistentVolumeClaims pour Redis
- Implémenter des sauvegardes régulières des données
- Configurer des stratégies de rétention des données
- Utiliser des volumes persistants avec des classes de stockage appropriées

---

## 8. Authentification et Autorisation

**Exigence** : Mécanisme d'authentification pour protéger les endpoints sensibles.

**Implémentation actuelle** :

- Système d'authentification basé sur des tokens stockés dans Redis
- Décorateur `@require_auth` pour protéger les endpoints
- Vérification des tokens via l'en-tête `Authorization`
- Clé par défaut `default_key` pour les tests

**Mécanisme d'authentification** :

```python
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Récupère la clé d'authentification depuis l'en-tête Authorization
        auth_key = request.headers.get("Authorization")

        # Vérifie si la clé est présente
        if not auth_key:
            return jsonify({"error": "Authorization header is missing"}), 401

        # Construit la clé Redis pour le token
        token_key = f"token:{auth_key}"

        # Vérifie si le token existe dans Redis
        if not redis_client.exists(token_key):
            return jsonify({"error": "Unauthorized: Invalid token"}), 401

        # Optionnel : Vérifie si le token a des informations valides
        token_data = redis_client.hgetall(token_key)
        if not token_data:
            return jsonify({"error": "Unauthorized: Token data is invalid"}), 401

        # Si tout est valide, exécute la fonction décorée
        return f(*args, **kwargs)
    return decorated
```

**Endpoints protégés** :

- `POST /quotes` - Ajout de citations
- `DELETE /quotes/<id>` - Suppression de citations
- `POST /users` - Création d'utilisateurs
- `GET /users` - Récupération des utilisateurs

**Améliorations possibles** :

- Implémenter un système d'authentification plus robuste (JWT, OAuth2)
- Ajouter des rôles et permissions (RBAC)
- Implémenter la rotation des tokens
- Ajouter des mécanismes de refresh token
- Implémenter l'authentification par identifiant/mot de passe en base de données

---

## 9. Sécurité du réseau

**Implémentation actuelle** :

- Utilisation de Docker networks pour isoler les services
- Configuration de Traefik comme reverse proxy
- Isolation des services dans un namespace Kubernetes dédié

**Configuration réseau** :

```yaml
networks:
  proxy:
    name: proxy
```

**Améliorations possibles** :

- Implémenter des NetworkPolicies Kubernetes pour restreindre le trafic entre pods
- Configurer des règles de pare-feu spécifiques
- Utiliser des certificats TLS pour le trafic interne
- Implémenter des VPN pour l'accès aux environnements de production

---

## 10. Surveillance et journalisation

**Implémentation actuelle** :

- Health checks configurés dans les Dockerfiles
- Commandes de logs disponibles dans le Makefile
- Journalisation basique dans les applications Flask

**Améliorations possibles** :

- Implémenter un système de logging centralisé (ELK, Loki)
- Configurer des alertes pour les événements de sécurité
- Implémenter des métriques de sécurité et des tableaux de bord
- Configurer des audits de sécurité réguliers

---

## 11. Observations et limites

### Limites actuelles

- **Limite mono-nœud** : En environnement mono-nœud, la montée en charge est limitée par les ressources de la VM. En multi-nœuds, utiliser des `HorizontalPodAutoscaler` et des `NodeAffinity`.
- **Authentification** : L’authentification par identifiant/mot de passe en base de données n’a pas été implémentée (bonus non réalisé).
- **Rate Limiting** : Le rate limiting dans Traefik est commenté et non activé dans la configuration actuelle.
- **Secrets** : Les secrets sont actuellement définis en clair dans les manifests Kubernetes.
- **Persistent Volumes** : Pas de configuration explicite de volumes persistants pour Redis.

### Bonnes pratiques mises en place

- Utilisation d'images Docker minimales et sécurisées
- Exécution des applications avec des utilisateurs non-root
- Isolation des services dans des namespaces Kubernetes
- Utilisation de tags d'images immutables
- Intégration de Trivy pour les scans de sécurité
- Mécanisme d'authentification basé sur tokens
- Configuration de health checks

### Recommandations pour l'amélioration

1. **Priorité élevée** :
   - Externaliser les secrets dans des Secrets Kubernetes ou un gestionnaire de secrets
   - Activer et configurer le rate limiting dans Traefik
   - Implémenter des PersistentVolumeClaims pour Redis
   - Configurer des NetworkPolicies Kubernetes

2. **Priorité moyenne** :
   - Implémenter un système d'authentification plus robuste (JWT)
   - Ajouter des rôles et permissions (RBAC)
   - Configurer un système de logging centralisé
   - Implémenter des sauvegardes régulières

3. **Priorité basse** :
   - Intégrer Trivy dans un pipeline CI/CD automatisé
   - Configurer des alertes de sécurité
   - Implémenter des métriques et tableaux de bord de sécurité
   - Configurer des audits de sécurité réguliers

---

## 12. Commandes utiles pour la sécurité

### Installation de Trivy

```bash
make install-trivy
```

### Exécution des tests de sécurité

```bash
make test-securiter
```

### Scan des vulnérabilités

```bash
trivy fs --scanners vuln --scanners misconfig,vuln .
```

### Scan des secrets

```bash
trivy fs --scanners secret .
```

### Scan des images Docker

```bash
trivy image --scanners vuln,misconfig sae503-kc-md-quotes:latest
```

### Vérification des déploiements Kubernetes

```bash
kubectl get pods -n haddock
kubectl get services -n haddock
kubectl get secrets -n haddock
```
