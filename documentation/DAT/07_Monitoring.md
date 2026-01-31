# 6. Monitoring et Maintenance

## 6.1 Surveillance

### 6.1.1 Surveillance des services

#### 6.1.1.1 Commandes kubectl

```bash
# Surveillance des pods
kubectl get pods -n haddock -w

# Surveillance des événements
kubectl get events -n haddock --sort-by='.metadata.creationTimestamp'

# Surveillance des ressources
kubectl top pods -n haddock
kubectl top nodes

# Surveillance des déploiements
kubectl get deployments -n haddock
kubectl describe deployment <nom-du-deployment> -n haddock
```

#### 6.1.1.2 Commandes Docker

```bash
# Surveillance des conteneurs
docker ps
watch docker ps

# Surveillance des ressources
docker stats

# Surveillance des logs
docker logs -f <nom-du-conteneur>
```

### 6.1.2 Dashboard Traefik

**Accès** : <http://localhost:8080/dashboard/>

**Fonctionnalités** :

- Visualisation des routes configurées
- Statistiques de trafic
- État des services
- Configuration actuelle

**Configuration** :

```yaml
# Dans le fichier docker-compose.yaml
services:
  traefik:
    # ...
    command:
      - "--api.insecure=true"  # Active le dashboard
      - "--api.dashboard=true"
    ports:
      - "8080:8080"  # Port du dashboard
```

### 6.1.3 Surveillance des endpoints

**Health checks** :

```bash
# Vérification de santé des services
curl http://localhost/quotes/health
curl http://localhost/users/health
curl http://localhost/search/health

# Script de surveillance
while true; do
    echo "$(date) - Quotes: $(curl -s http://localhost/quotes/health | jq -r '.message')"
    echo "$(date) - Users: $(curl -s http://localhost/users/health | jq -r '.message')"
    echo "$(date) - Search: $(curl -s http://localhost/search/health | jq -r '.message')"
    sleep 5
end
```

## 6.2 Journalisation

### 6.2.1 Journalisation des applications

#### 6.2.1.1 Configuration Flask

```python
import logging
from logging.handlers import RotatingFileHandler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Handler pour les fichiers
file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024 * 1024 * 5,  # 5 MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Ajout du handler
app.logger.addHandler(file_handler)

# Exemple d'utilisation
@app.route('/quotes', methods=['GET'])
def get_quotes():
    app.logger.info('Récupération des citations')
    try:
        quotes = redis_client.smembers("quotes")
        app.logger.debug(f'Trouvé {len(quotes)} citations')
        return jsonify([redis_client.hgetall(quote) for quote in quotes]), 200
    except Exception as e:
        app.logger.error(f'Erreur lors de la récupération des citations: {str(e)}')
        return jsonify({"error": "Internal server error"}), 500
```

#### 6.2.1.2 Niveaux de journalisation

| Niveau       | Utilisation                                   |
|--------------|-----------------------------------------------|
| DEBUG        | Informations de débogage détaillées           |
| INFO         | Informations générales sur le fonctionnement  |
| WARNING      | Avertissements et situations inhabituelles    |
| ERROR        | Erreurs qui affectent une opération           |
| CRITICAL     | Erreurs critiques nécessitant une intervention|

### 6.2.2 Journalisation Kubernetes

#### 6.2.2.1 Récupération des logs

```bash
# Logs d'un pod spécifique
kubectl logs <nom-du-pod> -n haddock

# Logs en temps réel
kubectl logs -f <nom-du-pod> -n haddock

# Logs des conteneurs précédents
kubectl logs <nom-du-pod> -n haddock --previous

# Logs avec sélection
kubectl logs -l app=quotes-service -n haddock

# Logs avec timestamp
kubectl logs --timestamps <nom-du-pod> -n haddock
```

#### 6.2.2.2 Journalisation centralisée (à implémenter)

**Options** :

1. **EFK Stack** (Elasticsearch, Fluentd, Kibana)
2. **Loki + Promtail + Grafana**
3. **Fluent Bit + Elasticsearch**

**Exemple de configuration Fluentd** :

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: haddock
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
      logstash_prefix kubernetes
      include_tag_key true
      type_name fluentd
    </match>
```

### 6.2.3 Rotation des logs

#### 6.2.3.1 Configuration dans les conteneurs

```dockerfile
# Dans le Dockerfile
RUN apt-get update && apt-get install -y logrotate

COPY logrotate.conf /etc/logrotate.conf
COPY logrotate.d/app /etc/logrotate.d/app

# Configuration logrotate
# /etc/logrotate.d/app
/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
```

#### 6.2.3.2 Rotation manuelle

```bash
# Rotation manuelle des logs
logrotate -f /etc/logrotate.conf

# Vérification
ls -la /app/logs/
```

## 6.3 Maintenance

### 6.3.1 Maintenance préventive

#### 6.3.1.1 Plan de maintenance

| Tâche                          | Fréquence       | Responsable      |
|--------------------------------|-----------------|------------------|
| Vérification des logs          | Quotidienne     | Équipe DevOps    |
| Mise à jour des dépendances    | Hebdomadaire    | Équipe Dev       |
| Sauvegarde des données         | Quotidienne     | Équipe DevOps    |
| Scan de sécurité               | Hebdomadaire    | Équipe Sécurité  |
| Vérification des performances  | Quotidienne     | Équipe DevOps    |
| Nettoyage des ressources       | Mensuelle       | Équipe DevOps    |

#### 6.3.1.2 Checklist de maintenance

```markdown
- [ ] Vérifier l'état des pods Kubernetes
- [ ] Vérifier les logs des applications
- [ ] Vérifier l'espace disque
- [ ] Vérifier la mémoire disponible
- [ ] Vérifier les connexions Redis
- [ ] Exécuter les tests de santé
- [ ] Vérifier les sauvegardes
- [ ] Scanner les vulnérabilités
- [ ] Mettre à jour la documentation
```

### 6.3.2 Mises à jour

#### 6.3.2.1 Processus de mise à jour

1. **Planification** : Identifier les composants à mettre à jour
2. **Test** : Tester les mises à jour dans un environnement de staging
3. **Sauvegarde** : Sauvegarder les données et configurations
4. **Déploiement** : Appliquer les mises à jour en production
5. **Vérification** : Vérifier le bon fonctionnement
6. **Documentation** : Mettre à jour la documentation

#### 6.3.2.2 Mise à jour des images Docker

```bash
# Mise à jour d'une image
docker pull redis:8

# Reconstruction des images personnalisées
docker build -t kitami1/sae503-quotes:v1.1.0 -f citations_haddock/quotes/Dockerfile citations_haddock

# Mise à jour du déploiement
kubectl set image deployment/quotes-service quotes-service=kitami1/sae503-quotes:v1.1.0 -n haddock
```

### 6.3.3 Nettoyage

#### 6.3.3.1 Nettoyage Kubernetes

```bash
# Suppression des pods terminés
kubectl delete pods --field-selector=status.phase==Succeeded -n haddock
kubectl delete pods --field-selector=status.phase==Failed -n haddock

# Nettoyage des images non utilisées
kubectl get images | grep none | awk '{print $1}' | xargs -I {} kubectl delete image {}

# Nettoyage des ressources inutilisées
kubectl delete --dry-run=client -o yaml $(kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n haddock) | kubectl delete -f -
```

#### 6.3.3.2 Nettoyage Docker

```bash
# Nettoyage des conteneurs
docker container prune

# Nettoyage des images
docker image prune -a

# Nettoyage des volumes
docker volume prune

# Nettoyage complet
docker system prune -a --volumes
```

## 6.4 Sauvegardes

### 6.4.1 Stratégie de sauvegarde

#### 6.4.1.1 Politique de sauvegarde

| Type de données       | Fréquence   | Rétention | Méthode                  |
|-----------------------|-------------|-----------|--------------------------|
| Données Redis         | Quotidienne | 7 jours   | Sauvegarde RDB           |
| Configurations K8s    | Quotidienne | 30 jours  | Export YAML              |
| Images Docker         | Hebdomadaire| 4 semaines| Registry privé           |
| Code source           | Continue    | Illimitée | GitHub                   |
| Logs                  | Quotidienne | 30 jours  | Archivage compressé      |

#### 6.4.1.2 Plan de reprise d'activité

1. **RTO (Recovery Time Objective)** : 1 heure
2. **RPO (Recovery Point Objective)** : 24 heures
3. **Priorité** : Données > Configurations > Applications

### 6.4.2 Sauvegarde des données Redis

#### 6.4.2.1 Sauvegarde manuelle

```bash
# Sauvegarde RDB
kubectl exec -it <redis-pod> -n haddock -- redis-cli save
kubectl exec -it <redis-pod> -n haddock -- redis-cli bgsave

# Copie du fichier de sauvegarde
kubectl cp haddock/<redis-pod>:/data/dump.rdb ./backup/redis-$(date +%Y%m%d).rdb
```

#### 6.4.2.2 Sauvegarde automatique (à implémenter)

```yaml
# CronJob Kubernetes pour sauvegarde automatique
apiVersion: batch/v1
kind: CronJob
metadata:
  name: redis-backup
  namespace: haddock
spec:
  schedule: "0 2 * * *"  # Tous les jours à 2h
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: redis-backup
            image: redis:8
            command:
            - /bin/sh
            - -c
            - "redis-cli -h backend-redis save && cp /data/dump.rdb /backup/redis-$(date +%Y%m%d).rdb"
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
```

### 6.4.3 Sauvegarde des configurations Kubernetes

#### 6.4.3.1 Export complet

```bash
# Sauvegarde de tous les objets Kubernetes
kubectl get all -n haddock -o yaml > backup/haddock-full-$(date +%Y%m%d).yaml

# Sauvegarde des objets spécifiques
kubectl get deployments,services,ingress -n haddock -o yaml > backup/haddock-core-$(date +%Y%m%d).yaml

# Sauvegarde des secrets
kubectl get secrets -n haddock -o yaml > backup/haddock-secrets-$(date +%Y%m%d).yaml
```

#### 6.4.3.2 Restauration

```bash
# Restauration à partir d'une sauvegarde
kubectl apply -f backup/haddock-full-20240101.yaml

# Vérification
kubectl get all -n haddock
```

### 6.4.4 Sauvegarde du code source

#### 6.4.4.1 Stratégie Git

```bash
# Commit régulier
git add .
git commit -m "Sauvegarde automatique - $(date +%Y%m%d)"
git push origin main

# Tag des versions importantes
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

#### 6.4.4.2 Archivage

```bash
# Création d'une archive
tar -czvf sae503-backup-$(date +%Y%m%d).tar.gz .

# Chiffrement (optionnel)
gpg --encrypt --recipient user@example.com sae503-backup-$(date +%Y%m%d).tar.gz
```

## 6.5 Alertes et notifications

### 6.5.1 Configuration des alertes (à implémenter)

#### 6.5.1.1 Alertes Kubernetes

```yaml
# Exemple de configuration avec Prometheus Operator
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: haddock-alerts
  namespace: haddock
spec:
  groups:
  - name: haddock.rules
    rules:
    - alert: PodDown
      expr: kube_pod_status_phase{phase="Running", namespace="haddock"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Pod {{ $labels.pod }} is down"
        description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has been down for more than 5 minutes"
    
    - alert: HighMemoryUsage
      expr: (sum(container_memory_working_set_bytes{namespace="haddock"}) by (pod) / sum(container_spec_memory_limit_bytes{namespace="haddock"}) by (pod)) * 100 > 80
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage in pod {{ $labels.pod }}"
        description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has been using more than 80% of its memory limit for 10 minutes"
```

#### 6.5.1.2 Intégration avec des outils externes

**Options** :

1. **Slack** : Notifications via webhooks
2. **Email** : Envoi d'emails via SMTP
3. **PagerDuty** : Alertes professionnelles
4. **Discord** : Notifications pour les équipes

### 6.5.2 Journal des incidents

#### 6.5.2.1 Modèle de rapport d'incident

```markdown
# Rapport d'incident - [ID]

## Résumé
- **Date** : [Date et heure]
- **Service affecté** : [Nom du service]
- **Impact** : [Haut/Moyen/Faible]
- **Durée** : [Durée de l'incident]

## Chronologie
- [HH:MM] : Détection de l'incident
- [HH:MM] : Début de l'investigation
- [HH:MM] : Identification de la cause
- [HH:MM] : Application du correctif
- [HH:MM] : Résolution complète

## Cause racine
[Description détaillée de la cause]

## Actions correctives
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Actions préventives
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Responsables
- **Détection** : [Nom]
- **Résolution** : [Nom]
- **Communication** : [Nom]

## Pièces jointes
- [Logs pertinents]
- [Screenshots]
- [Autres preuves]
```

#### 6.5.2.2 Exemple de rapport

```markdown
# Rapport d'incident - INC-2024-001

## Résumé
- **Date** : 2024-01-15 14:30:00
- **Service affecté** : Quotes Service
- **Impact** : Moyen (certains utilisateurs affectés)
- **Durée** : 45 minutes

## Chronologie
- 14:30 : Détection via les alertes de monitoring
- 14:32 : Début de l'investigation
- 14:40 : Identification d'un problème de connexion Redis
- 14:45 : Redémarrage du pod Redis
- 15:15 : Résolution complète et vérification

## Cause racine
Le pod Redis a atteint sa limite de mémoire et a été tué par le OOM Killer de Kubernetes. La configuration initiale ne prévoyait pas suffisamment de mémoire pour le cache.

## Actions correctives
1. Redémarrage du pod Redis
2. Augmentation temporaire des limites de mémoire
3. Vérification de l'intégrité des données

## Actions préventives
1. Augmenter les limites de mémoire dans la configuration Kubernetes
2. Configurer des alertes pour l'utilisation de la mémoire
3. Implémenter un mécanisme de cache plus efficace
4. Documenter la procédure de redémarrage

## Responsables
- **Détection** : Système de monitoring
- **Résolution** : Équipe DevOps
- **Communication** : Équipe Support

## Pièces jointes
- logs/quotes-service-20240115.log
- screenshots/memory-usage.png
```

## 6.6 Métriques et indicateurs

### 6.6.1 Indicateurs clés de performance (KPI)

| Indicateur                           | Objectif          | Mesure actuelle | Fréquence      |
|--------------------------------------|-------------------|-----------------|----------------|
| Disponibilité des services           | 99.9%             | 99.8%           | Temps réel     |
| Temps de réponse moyen               | < 200ms           | 180ms           | Toutes les 5min|
| Taux d'erreur                        | < 1%              | 0.5%            | Toutes les 5min|
| Utilisation CPU moyenne              | < 70%             | 65%             | Toutes les 5min|
| Utilisation mémoire moyenne          | < 80%             | 75%             | Toutes les 5min|
| Nombre de requêtes par seconde       | -                 | 15 req/s        | Toutes les 5min|
| Temps de récupération après incident | < 30min           | 25min           | Par incident   |

### 6.6.2 Tableau de bord (à implémenter)

**Options** :

1. **Grafana** : Tableaux de bord personnalisables
2. **Kibana** : Visualisation des logs
3. **Prometheus + Grafana** : Solution complète
4. **Custom dashboard** : Solution maison

**Exemple de configuration Grafana** :

```json
{
  "title": "SAE 5.03 - Overview",
  "panels": [
    {
      "title": "Service Availability",
      "type": "singlestat",
      "targets": [
        {
          "expr": "sum(up{namespace=\"haddock\"}) / count(up{namespace=\"haddock\"}) * 100",
          "format": "time_series",
          "interval": "",
          "legendFormat": "",
          "refId": "A"
        }
      ]
    },
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{namespace=\"haddock\"}[5m]))",
          "format": "time_series",
          "interval": "",
          "legendFormat": "{{pod}}",
          "refId": "A"
        }
      ]
    }
  ],
  "templating": {
    "list": [
      {
        "name": "namespace",
        "query": "haddock",
        "type": "constant"
      }
    ]
  }
}
```

### 6.6.3 Collecte de métriques

#### 6.6.3.1 Métriques applicatives

```python
# Dans les services Flask
from prometheus_client import make_wsgi_app, Counter, Gauge, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Configuration des métriques
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'HTTP request latency', ['method', 'endpoint'])
IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP requests in progress', ['method', 'endpoint'])

# Middleware pour la collecte
def before_request():
    request.start_time = time.time()
    IN_PROGRESS.labels(request.method, request.path).inc()

def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
    IN_PROGRESS.labels(request.method, request.path).dec()
    return response

# Ajout du middleware
app.before_request(before_request)
app.after_request(after_request)

# Exposition des métriques
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
```

#### 6.6.3.2 Métriques système

```bash
# Métriques CPU
kubectl top pods -n haddock --containers

# Métriques mémoire
kubectl top pods -n haddock --sort-by=memory

# Métriques réseau
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/namespaces/haddock/pods/*/network" | jq .
```

## 6.7 Documentation et procédures

### 6.7.1 Procédures opérationnelles

#### 6.7.1.1 Procédure de redémarrage

```markdown
# Procédure de redémarrage des services

## Prérequis
- Accès à kubectl
- Permissions suffisantes

## Étapes

1. **Vérification de l'état actuel**
   ```bash
   kubectl get pods -n haddock
   ```

2. **Identification du pod à redémarrer**

```bash
kubectl get pods -n haddock | grep <service>
```

1. **Redémarrage du pod**

   ```bash
   kubectl delete pod <nom-du-pod> -n haddock
   ```

2. **Vérification du redémarrage**

   ```bash
   kubectl get pods -n haddock -w
   ```

3. **Vérification des logs**

   ```bash
   kubectl logs <nouveau-pod> -n haddock
   ```

4. **Test fonctionnel**

   ```bash
   curl http://localhost/<service>/health
   ```

## En cas d'échec

- Vérifier les logs
- Vérifier les ressources disponibles
- Contacter l'équipe de support

```txt
#### 6.7.1.2 Procédure de mise à l'échelle

```markdown
# Procédure de mise à l'échelle

## Mise à l'échelle manuelle

1. **Vérification de la charge actuelle**
   ```bash
   kubectl top pods -n haddock
   ```

2. **Mise à l'échelle**

   ```bash
   kubectl scale deployment <deployment> --replicas=<nombre> -n haddock
   ```

3. **Vérification**

   ```bash
   kubectl get pods -n haddock
   kubectl get hpa -n haddock
   ```

## Configuration de l'autoscaling

1. **Création de l'HPA**

   ```bash
   kubectl autoscale deployment <deployment> --min=<min> --max=<max> --cpu-percent=<pourcentage> -n haddock
   ```

2. **Vérification**

   ```bash
   kubectl get hpa -n haddock -w
   ```

3. **Ajustement**

   ```bash
   kubectl edit hpa <nom-hpa> -n haddock
   ```

```txt

### 6.7.2 Documentation des incidents

#### 6.7.2.1 Modèle de ticket d'incident

```markdown
# Ticket d'incident - [ID]

## Informations générales
- **Date de création** : [Date/Heure]
- **Créé par** : [Nom]
- **Priorité** : [Haute/Moyenne/Faible]
- **Service affecté** : [Nom du service]

## Description
[Description détaillée du problème]

## Symptômes
- [Symptôme 1]
- [Symptôme 2]
- [Symptôme 3]

## Étapes de reproduction
1. [Étape 1]
2. [Étape 2]
3. [Étape 3]

## Impact
- **Utilisateurs affectés** : [Nombre/Description]
- **Fonctionnalités affectées** : [Liste]
- **Sévérité** : [Haute/Moyenne/Faible]

## Investigation
- **Logs pertinents** :
  ```
  [Extraits de logs]
  ```
- **Métriques** :
  - CPU : [Valeur]%
  - Mémoire : [Valeur]%
  - Temps de réponse : [Valeur]ms

## Résolution
- **Cause racine** : [Description]
- **Solution appliquée** : [Description]
- **Date de résolution** : [Date/Heure]

## Vérification
- **Tests effectués** : [Liste]
- **Résultats** : [Succès/Échec]
- **Validation** : [Nom de la personne]

## Actions préventives
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Historique
- [Date/Heure] : [Événement]
- [Date/Heure] : [Événement]
- [Date/Heure] : [Événement]
```

#### 6.7.2.2 Base de connaissances

```markdown
# Base de connaissances - Problèmes courants

## 1. Pod en CrashLoopBackOff

### Symptômes
- Pod redémarre en boucle
- État "CrashLoopBackOff" dans kubectl get pods

### Causes possibles
- Erreur dans le code de l'application
- Configuration incorrecte
- Ressources insuffisantes
- Dépendances manquantes

### Solutions
1. **Vérifier les logs**
   ```bash
   kubectl logs <nom-du-pod> -n haddock --previous
   ```

2. **Vérifier la configuration**
   ```bash
   kubectl describe pod <nom-du-pod> -n haddock
   ```

3. **Augmenter les ressources**
   ```yaml
   resources:
     limits:
       cpu: "1"
       memory: "512Mi"
     requests:
       cpu: "500m"
       memory: "256Mi"
   ```

4. **Redémarrer le pod**
   ```bash
   kubectl delete pod <nom-du-pod> -n haddock
   ```

## 2. Problème de connexion Redis

### Symptômes

- Erreurs "Connection refused" dans les logs
- Services incapables de se connecter à Redis

### Causes possibles

- Redis non démarré
- Problème de réseau
- Configuration incorrecte

### Solutions

1. **Vérifier l'état de Redis**
   ```bash
   kubectl get pods -n haddock | grep redis
   ```

2. **Tester la connectivité**
   ```bash
   kubectl exec -it <quotes-pod> -n haddock -- ping backend-redis
   ```

3. **Vérifier la configuration**
   ```bash
   kubectl describe service backend-redis -n haddock
   ```

4. **Redémarrer Redis**
   ```bash
   kubectl delete pod <redis-pod> -n haddock
   ```

## 3. Performances dégradées

### Symptômes

- Temps de réponse élevés
- Utilisation CPU/Mémoire élevée
- Requêtes timeout

### Causes possibles

- Charge trop importante
- Ressources insuffisantes
- Requêtes inefficaces

### Solutions

1. **Vérifier les métriques**

   ```bash
   kubectl top pods -n haddock
   ```

2. **Mettre à l'échelle**
   ```bash
   kubectl scale deployment quotes-service --replicas=3 -n haddock
   ```

3. **Optimiser les requêtes**
   - Ajouter des indexes
   - Implémenter du caching
   - Optimiser le code

4. **Configurer l'autoscaling**

   ```bash
   kubectl autoscale deployment quotes-service --min=2 --max=5 --cpu-percent=80 -n haddock
   ```

```

## 6.8 Améliorations continues

### 6.8.1 Roadmap des améliorations

| Amélioration                          | Priorité | Échéance    | Responsable      | Statut          |
|---------------------------------------|----------|-------------|------------------|-----------------|
| Implémentation de Prometheus/Grafana   | Haute    | Q1 2024     | Équipe DevOps    | À faire         |
| Configuration de l'autoscaling        | Moyenne  | Q1 2024     | Équipe DevOps    | En cours        |
| Sauvegardes automatiques Redis         | Haute    | Q1 2024     | Équipe DevOps    | À faire         |
| Journalisation centralisée             | Moyenne  | Q2 2024     | Équipe DevOps    | Planifié        |
| Alertes et notifications               | Haute    | Q1 2024     | Équipe DevOps    | À faire         |
| Optimisation des performances          | Moyenne  | Q2 2024     | Équipe Dev       | Planifié        |
| Documentation des procédures           | Haute    | Q1 2024     | Équipe DevOps    | En cours        |

### 6.8.2 Revue post-incident

**Processus** :
1. **Identification** : Analyser l'incident et sa cause racine
2. **Documentation** : Rédiger un rapport d'incident complet
3. **Amélioration** : Identifier les actions préventives
4. **Implémentation** : Mettre en place les correctifs
5. **Vérification** : Tester les améliorations
6. **Documentation** : Mettre à jour la documentation

**Exemple de revue** :
```markdown
# Revue post-incident - INC-2024-001

## Résumé
- **Incident** : Indisponibilité du Quotes Service
- **Date** : 2024-01-15
- **Durée** : 45 minutes
- **Impact** : Moyen

## Cause racine
Limite de mémoire insuffisante pour le pod Redis, entraînant un OOM kill.

## Leçons apprises
1. Les limites de mémoire doivent être réalistes
2. Le monitoring des ressources est crucial
3. Les alertes doivent être configurées pour les situations critiques

## Actions correctives
1. ✅ Augmentation des limites de mémoire pour Redis
2. ✅ Configuration d'alertes pour l'utilisation de la mémoire
3. ✅ Documentation de la procédure de redémarrage
4. ⏳ Implémentation de l'autoscaling pour Redis
5. ⏳ Revue des limites de mémoire pour tous les services

## Améliorations futures
1. Mettre en place un système de monitoring complet
2. Configurer des alertes proactives
3. Implémenter des tests de charge réguliers
4. Documenter toutes les procédures d'urgence

## Responsables
- **Revue** : Équipe DevOps
- **Suivi** : Chef de projet
- **Validation** : Responsable technique
```

### 6.8.3 Indicateurs d'amélioration

| Indicateur                          | Cible 2024 | Actuel    | Progression  |
|-------------------------------------|------------|-----------|--------------|
| Temps moyen de résolution           | < 30min    | 45min     | 🔴 En retard |
| Disponibilité des services          | 99.95%     | 99.8%     | 🟡 En cours  |
| Couverture des tests                | 90%        | 75%       | 🟡 En cours  |
| Documentation complète              | 100%       | 80%       | 🟡 En cours  |
| Temps de réponse moyen              | < 150ms    | 180ms     | 🟡 En cours  |
| Taux de détection proactive         | 80%        | 40%       | 🔴 En retard |

## 6.9 Conclusion

Le monitoring et la maintenance sont des aspects critiques pour assurer la fiabilité et la disponibilité de l'application. Les éléments clés à retenir sont :

1. **Surveillance proactive** : Détecter les problèmes avant qu'ils n'affectent les utilisateurs
2. **Journalisation complète** : Avoir des logs détaillés pour le dépannage
3. **Sauvegardes régulières** : Protéger contre la perte de données
4. **Documentation** : Maintenir une documentation à jour des procédures
5. **Amélioration continue** : Apprendre des incidents et améliorer constamment

**Recommandations** :

- Implémenter un système de monitoring complet (Prometheus + Grafana)
- Configurer des alertes proactives pour les situations critiques
- Automatiser les sauvegardes et les tests de restauration
- Documenter toutes les procédures opérationnelles
- Effectuer des revues régulières des incidents et des performances

La mise en place de ces pratiques permettra d'assurer la stabilité, la disponibilité et la performance de l'application à long terme.
