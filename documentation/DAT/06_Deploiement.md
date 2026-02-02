# 5. Déploiement et Configuration

## 5.1 Prérequis

### 5.1.1 Matériel

- **Machine virtuelle ou physique** :
  - CPU : 2 cœurs minimum (4 recommandés)
  - RAM : 4 Go minimum (8 Go recommandés)
  - Stockage : 20 Go minimum
  - Système d'exploitation : Linux (Ubuntu 22.04 LTS recommandé)

### 5.1.2 Logiciels

- **Docker** : Version 20.10 ou supérieure
- **Kubernetes** : Version 1.25 ou supérieure
- **kubectl** : Outil de ligne de commande Kubernetes
- **Helm** : (Optionnel) Version 3.x pour les charts
- **Trivy** : (Recommandé) Pour les scans de sécurité
- **Git** : Pour le contrôle de version
- **Python** : Version 3.12 pour le développement
- **pip** : Gestionnaire de paquets Python

### 5.1.3 Accès réseau

- Accès Internet pour télécharger les images Docker
- Ports ouverts :
  - 80 (HTTP)
  - 5000 (Accès alternatif)
  - 8080 (Dashboard Traefik)

## 5.2 Installation

### 5.2.1 Installation de Docker

```bash
# Mise à jour des paquets
sudo apt-get update

# Installation des dépendances
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajout de la clé GPG officielle de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configuration du repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation de Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Vérification
sudo docker run hello-world
```

### 5.2.2 Installation de Kubernetes

#### 5.2.2.1 Installation de kubeadm, kubelet et kubectl

```bash
# Désactivation du swap
sudo swapoff -a
sudo sed -i '/ swap / s/^(.*)$/#\1/g' /etc/fstab

# Installation des dépendances
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

# Ajout de la clé GPG de Kubernetes
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# Ajout du repository Kubernetes
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Installation des paquets Kubernetes
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Activation des services
sudo systemctl enable kubelet
```

#### 5.2.2.2 Initialisation du cluster Kubernetes

```bash
# Initialisation du cluster (pour le nœud maître)
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Configuration de kubectl pour l'utilisateur courant
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Installation du réseau (ex: Flannel)
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# Vérification
kubectl get nodes
kubectl get pods --all-namespaces
```

### 5.2.3 Installation de Trivy (optionnel)

```bash
# Installation des dépendances
sudo apt-get install -y wget apt-transport-https gnupg lsb-release

# Ajout de la clé GPG de Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

# Ajout du repository Trivy
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list

# Installation de Trivy
sudo apt-get update
sudo apt-get install -y trivy

# Vérification
trivy --version
```

## 5.3 Configuration

### 5.3.1 Configuration de l'environnement

#### 5.3.1.1 Variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# Configuration générale
PROJECT_NAME=sae503-kc-md
ENVIRONMENT=development

# Configuration Docker
DOCKER_NETWORK=proxy

# Configuration Kubernetes
KUBE_NAMESPACE=haddock

# Configuration des services
REDIS_HOST=backend-redis
REDIS_PORT=6379
REDIS_DB=0

# Configuration des microservices
APP_PORT=5000
ADMIN_KEY=["default_key"]

# Configuration Traefik
TRAEFIK_DASHBOARD_PORT=8080
TRAEFIK_HTTP_PORT=80
TRAEFIK_HADDOCK_PORT=5000
```

#### 5.3.1.2 Configuration des services

### 5.3.2 Configuration des microservices

#### 5.3.2.1 Users Service

Fichier `citations_haddock/users/config.py` :

```python
import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
    ADMIN_KEY = os.getenv("ADMIN_KEY", '["default_key"]')
    CSV_FILE_USERS = os.getenv("CSV_FILE_USERS", "initial_data_users.csv")
```

#### 5.3.2.2 Quotes Service

Fichier `citations_haddock/quotes/config.py` :

```python
import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
    CSV_FILE_QUOTES = os.getenv("CSV_FILE_QUOTES", "initial_data_quotes.csv")
```

#### 5.3.2.3 Search Service

Fichier `citations_haddock/search/config.py` :

```python
import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
```

### 5.3.3 Configuration de Traefik

Fichier `traefik-config.yaml` :

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: traefik-config
  namespace: haddock
data:
  traefik.yml: |
    api:
      insecure: true
      dashboard: true
    
    entryPoints:
      web:
        address: ":80"
      haddock:
        address: ":5000"
    
    providers:
      kubernetesCRD:
        namespaces:
          - haddock
    
    log:
      level: INFO
```

## 5.4 Déploiement

### 5.4.1 Déploiement avec Docker Compose

#### 5.4.1.1 Build des images

```bash
# Construction des images Docker
docker build -t kitami1/sae503-users -f citations_haddock/users/Dockerfile citations_haddock
docker build -t kitami1/sae503-quotes -f citations_haddock/quotes/Dockerfile citations_haddock
docker build -t kitami1/sae503-search -f citations_haddock/search/Dockerfile citations_haddock
```

#### 5.4.1.2 Lancement des services

```bash
# Démarrage des services
docker compose up -d

# Vérification
docker compose ps
```

### 5.4.2 Déploiement avec Kubernetes

#### 5.4.2.1 Création du namespace

```bash
# Création du namespace haddock
kubectl create namespace haddock

# Vérification
kubectl get namespaces
```

#### 5.4.2.2 Déploiement de Redis

```bash
# Application du fichier de déploiement Redis
kubectl apply -f kube/deployment.yaml

# Vérification
kubectl get pods -n haddock
kubectl get services -n haddock
```

#### 5.4.2.3 Déploiement des microservices

```bash
# Déploiement des services users, quotes et search
kubectl apply -f kube/deployment.yaml

# Vérification des pods
kubectl get pods -n haddock -w

# Vérification des services
kubectl get services -n haddock
```

#### 5.4.2.4 Déploiement de Traefik

```bash
# Déploiement de Traefik
kubectl apply -f kube/traefik.yaml

# Vérification
kubectl get pods -n haddock
kubectl get ingress -n haddock
```

### 5.4.3 Déploiement avec Helm (optionnel)

#### 5.4.3.1 Installation du chart

```bash
# Ajout du repository Helm (si nécessaire)
helm repo add haddock https://github.com/olivinfo/sae503-kc-md/haddock_kc_md

# Installation du chart
helm install haddock-app ./haddock_kc_md -n haddock
```

#### 5.4.3.2 Configuration du chart

```bash
# Mise à jour des valeurs
helm upgrade haddock-app ./haddock_kc_md -n haddock -f haddock_kc_md/values.yaml
```

## 5.5 Vérification

### 5.5.1 Vérification des services

#### 5.5.1.1 Vérification avec kubectl

```bash
# Liste des pods
kubectl get pods -n haddock

# Liste des services
kubectl get services -n haddock

# Liste des ingress
kubectl get ingress -n haddock

# Détails d'un pod spécifique
kubectl describe pod <nom-du-pod> -n haddock

# Logs d'un pod
kubectl logs <nom-du-pod> -n haddock
```

#### 5.5.1.2 Vérification avec Docker

```bash
# Liste des conteneurs
docker ps

# Logs d'un conteneur
docker logs <nom-du-conteneur>

# Statistiques
docker stats
```

### 5.5.2 Tests fonctionnels

#### 5.5.2.1 Test des endpoints

```bash
# Test du service users
curl http://localhost/users

# Test du service quotes
curl http://localhost/quotes

# Test du service search
curl http://localhost/search

# Test avec authentification
curl -H "Authorization: default_key" -X POST http://localhost/quotes -H "Content-Type: application/json" -d '{"user_id": "1", "quote": "Test citation"}'
```

#### 5.5.2.2 Test du dashboard Traefik

```bash
# Accès au dashboard
curl http://localhost:8080/api

# Ou via navigateur : http://localhost:8080/dashboard/
```

### 5.5.3 Tests de sécurité

#### 5.5.3.1 Scan avec Trivy

```bash
# Scan des vulnérabilités
trivy fs --scanners vuln .

# Scan des secrets
trivy fs --scanners secret .

# Scan des images Docker
trivy image kitami1/sae503-quotes:1.0.0

# Scan des configurations Kubernetes
trivy config kube/
```

#### 5.5.3.2 Vérification des secrets

```bash
# Liste des secrets Kubernetes
kubectl get secrets -n haddock

# Vérification des variables d'environnement
kubectl describe pod <nom-du-pod> -n haddock | grep -A 10 "Environment"
```

## 5.6 Gestion du cycle de vie

### 5.6.1 Mise à jour

#### 5.6.1.1 Mise à jour des images

```bash
# Mise à jour d'une image Docker
docker build -t kitami1/sae503-quotes:v1.1.0 -f citations_haddock/quotes/Dockerfile citations_haddock

# Mise à jour du déploiement Kubernetes
kubectl set image deployment/quotes-service quotes-service=kitami1/sae503-quotes:v1.1.0 -n haddock
```

#### 5.6.1.2 Rolling update

```bash
# Mise à jour progressive
kubectl rollout status deployment/quotes-service -n haddock

# Annulation d'une mise à jour
kubectl rollout undo deployment/quotes-service -n haddock
```

### 5.6.2 Mise à l'échelle

#### 5.6.2.1 Scaling manuel

```bash
# Mise à l'échelle d'un deployment
kubectl scale deployment quotes-service --replicas=3 -n haddock

# Vérification
kubectl get pods -n haddock
```

#### 5.6.2.2 Autoscaling

```bash
# Configuration de l'autoscaling
kubectl autoscale deployment quotes-service --min=2 --max=5 --cpu-percent=80 -n haddock

# Vérification
kubectl get hpa -n haddock
```

### 5.6.3 Sauvegarde et restauration

#### 5.6.3.1 Sauvegarde des données Redis

```bash
# Sauvegarde manuelle (à implémenter)
# redis-cli --rdb /backup/redis.dump

# Sauvegarde des configurations Kubernetes
kubectl get all -n haddock -o yaml > haddock-backup.yaml
```

#### 5.6.3.2 Restauration

```bash
# Restauration des configurations
kubectl apply -f haddock-backup.yaml

# Restauration des données Redis (à implémenter)
# redis-cli --load /backup/redis.dump
```

## 5.7 Dépannage

### 5.7.1 Problèmes courants

#### 5.7.1.1 Pods en état "Pending"

**Causes possibles** :

- Ressources insuffisantes
- Problème de réseau
- Configuration incorrecte

**Solutions** :

```bash
# Vérification des événements
kubectl get events -n haddock

# Description détaillée du pod
kubectl describe pod <nom-du-pod> -n haddock

# Vérification des ressources
kubectl top nodes
```

#### 5.7.1.2 Pods en état "CrashLoopBackOff"

**Causes possibles** :

- Erreur dans l'application
- Configuration incorrecte
- Problème de dépendances

**Solutions** :

```bash
# Vérification des logs
kubectl logs <nom-du-pod> -n haddock

# Redémarrage du pod
kubectl delete pod <nom-du-pod> -n haddock

# Vérification de la configuration
kubectl describe deployment <nom-du-deployment> -n haddock
```

#### 5.7.1.3 Problèmes de réseau

**Causes possibles** :

- Configuration incorrecte de Traefik
- Problème de DNS
- Règles de réseau bloquantes

**Solutions** :

```bash
# Vérification des services
kubectl get services -n haddock

# Test de connectivité
kubectl exec -it <nom-du-pod> -n haddock -- ping <autre-service>

# Vérification de Traefik
kubectl logs -l app=traefik -n haddock
```

### 5.7.2 Commandes utiles

```bash
# Redémarrage complet
kubectl delete namespace haddock
kubectl create namespace haddock
kubectl apply -f kube/

# Nettoyage Docker
docker system prune -a

# Réinitialisation de Kubernetes
kubeadm reset
```

## 5.8 Bonnes pratiques

### 5.8.1 Déploiement

1. **Utiliser des tags immutables** : Éviter les tags `latest`
2. **Vérifier les images** : Scanner avec Trivy avant déploiement
3. **Tests pré-déploiement** : Exécuter les tests unitaires et fonctionnels
4. **Déploiement progressif** : Utiliser les rolling updates
5. **Monitoring** : Vérifier les logs et métriques après déploiement

### 5.8.2 Sécurité

1. **Ne pas exposer les secrets** : Utiliser Kubernetes Secrets
2. **Limiter les privilèges** : Configurer le securityContext
3. **Isoler les environnements** : Utiliser des namespaces dédiés
4. **Mettre à jour régulièrement** : Images et dépendances
5. **Scanner régulièrement** : Vulnérabilités et secrets

### 5.8.3 Maintenance

1. **Documenter les changements** : Mettre à jour la documentation
2. **Sauvegarder régulièrement** : Configurations et données
3. **Monitorer les performances** : Utilisation des ressources
4. **Planifier les mises à jour** : Maintenance préventive
5. **Automatiser** : Utiliser des scripts et CI/CD

## 5.9 Scripts utiles

### 5.9.1 Script de déploiement complet

```bash
#!/bin/bash

# Script de déploiement complet

echo "Déploiement de l'application SAE 5.03..."

# Build des images
echo "Construction des images Docker..."
docker build -t kitami1/sae503-users -f citations_haddock/users/Dockerfile citations_haddock
docker build -t kitami1/sae503-quotes -f citations_haddock/quotes/Dockerfile citations_haddock
docker build -t kitami1/sae503-search -f citations_haddock/search/Dockerfile citations_haddock

# Création du namespace
echo "Création du namespace Kubernetes..."
kubectl create namespace haddock --dry-run=client -o yaml | kubectl apply -f -

# Déploiement
echo "Déploiement des services..."
kubectl apply -f kube/deployment.yaml

# Vérification
echo "Vérification du déploiement..."
kubectl get pods -n haddock -w

# Tests
echo "Exécution des tests..."
curl -s http://localhost/quotes | grep "healthy"

if [ $? -eq 0 ]; then
    echo "Déploiement réussi !"
else
    echo "Problème lors du déploiement"
    exit 1
fi
```

### 5.9.2 Script de nettoyage

```bash
#!/bin/bash

# Script de nettoyage

echo "Nettoyage de l'environnement..."

# Suppression du namespace
kubectl delete namespace haddock

# Nettoyage Docker
docker system prune -a -f

# Suppression des images
docker rmi kitami1/sae503-users kitami1/sae503-quotes kitami1/sae503-search

echo "Nettoyage terminé"
```

## 5.10 Documentation supplémentaire

- [Documentation Kubernetes](https://kubernetes.io/docs/home/)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation Traefik](https://doc.traefik.io/traefik/)
- [Documentation Redis](https://redis.io/documentation)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [SECURITY.md](../../../SECURITY.md) - Mesures de sécurité
- [Makefile](../../../Makefile) - Commandes utiles
