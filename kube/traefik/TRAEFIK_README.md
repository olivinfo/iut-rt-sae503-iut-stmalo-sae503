# Déploiement de Traefik en local

Ce guide explique comment déployer Traefik en local pour le projet SAE503.

## Prérequis

- Kubernetes (Minikube, Kind, ou Docker Desktop avec Kubernetes activé)
- kubectl installé et configuré
- Accès à un cluster Kubernetes local

## Structure des fichiers

```
.
├── traefik-config.yaml      # Configuration de Traefik
├── traefik-deployment.yaml  # Déploiement de Traefik
├── traefik-service.yaml     # Service pour Traefik
├── traefik-rbac.yaml        # Configuration RBAC pour Traefik
├── deploy-traefik.sh        # Script de déploiement
└── TRAEFIK_README.md        # Ce fichier
```

## Déploiement

### Méthode 1: Utilisation du script (recommandé)

```bash
./deploy-traefik.sh
```

### Méthode 2: Déploiement manuel

1. Créer la configuration RBAC:
   ```bash
   kubectl apply -f traefik-rbac.yaml
   ```

2. Créer la configuration Traefik:
   ```bash
   kubectl apply -f traefik-config.yaml
   ```

3. Déployer Traefik:
   ```bash
   kubectl apply -f traefik-deployment.yaml
   ```

4. Créer le service:
   ```bash
   kubectl apply -f traefik-service.yaml
   ```

## Accès aux services

- **Tableau de bord Traefik**: http://localhost:8080
- **Service Traefik (HTTP)**: http://localhost:80
- **Service Traefik (HTTPS)**: https://localhost:443

## Configuration

La configuration de Traefik est définie dans `traefik-config.yaml`:

- **Entrypoints**: web (80), websecure (443)
- **API Dashboard**: Activé sur le port 8080
- **Providers**: Kubernetes CRD et Ingress
- **Logging**: Niveau INFO

## Nettoyage

Pour supprimer Traefik et ses ressources:

```bash
kubectl delete -f traefik-service.yaml
kubectl delete -f traefik-deployment.yaml
kubectl delete -f traefik-config.yaml
kubectl delete -f traefik-rbac.yaml
```

## Dépannage

1. **Vérifier les logs**:
   ```bash
   kubectl logs -l app=traefik
   ```

2. **Vérifier les événements**:
   ```bash
   kubectl get events --sort-by='.metadata.creationTimestamp'
   ```

3. **Vérifier les pods**:
   ```bash
   kubectl get pods -l app=traefik
   ```

## Configuration avancée

Pour configurer des routes personnalisées, vous pouvez créer des fichiers Ingress ou utiliser les CRD Traefik. Exemple de base:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

## Notes

- Ce déploiement utilise l'image `traefik:v2.10`
- Le service est de type LoadBalancer pour un accès local facile
- Les permissions RBAC sont configurées pour permettre à Traefik de découvrir les services et ingress
