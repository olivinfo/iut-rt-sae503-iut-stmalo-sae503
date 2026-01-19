# Déploiement de Traefik en local avec Kustomize

Ce guide explique comment déployer Traefik en local pour le projet SAE503 en utilisant Kustomize.

## Prérequis

- Kubernetes (Minikube, Kind, ou Docker Desktop avec Kubernetes activé)
- kubectl installé et configuré (avec support Kustomize)
- Accès à un cluster Kubernetes local

## Structure des fichiers

```
traefik/
├── kustomization.yaml      # Configuration Kustomize principale
├── traefik-config.yaml     # Configuration de Traefik
├── traefik-deployment.yaml # Déploiement de Traefik
├── traefik-service.yaml    # Service pour Traefik
├── traefik-rbac.yaml       # Configuration RBAC pour Traefik
├── deploy-traefik-kustomize.sh # Script de déploiement avec Kustomize
└── README.md               # Ce fichier
```

## Déploiement avec Kustomize

### Méthode 1: Utilisation du script (recommandé)

```bash
cd traefik
./deploy-traefik-kustomize.sh
```

### Méthode 2: Déploiement direct avec kubectl

```bash
cd traefik
kubectl apply -k .
```

### Méthode 3: Déploiement manuel (sans Kustomize)

Si vous préférez ne pas utiliser Kustomize, vous pouvez toujours déployer manuellement:

```bash
cd traefik
kubectl apply -f traefik-rbac.yaml
kubectl apply -f traefik-config.yaml
kubectl apply -f traefik-deployment.yaml
kubectl apply -f traefik-service.yaml
```

## Avantages de Kustomize

1. **Gestion centralisée**: Toutes les ressources sont définies dans `kustomization.yaml`
2. **Labels communs**: Tous les objets ont automatiquement les labels `app: traefik` et `component: ingress-controller`
3. **Personnalisation facile**: Modification centralisée des images, namespaces, etc.
4. **Visualisation**: `kubectl kustomize .` montre la configuration finale avant application

## Accès aux services

- **Tableau de bord Traefik**: http://localhost:8080
- **Service Traefik (HTTP)**: http://localhost:80
- **Service Traefik (HTTPS)**: https://localhost:443
- **Namespace**: haddock

## Configuration

La configuration de Traefik est définie dans `traefik-config.yaml`:

- **Entrypoints**: web (80), websecure (443)
- **API Dashboard**: Activé sur le port 8080
- **Providers**: Kubernetes CRD et Ingress
- **Logging**: Niveau INFO

## Personnalisation avec Kustomize

Vous pouvez facilement personnaliser le déploiement en modifiant le `kustomization.yaml`:

### Changer l'image Traefik

```yaml
# Ajoutez ceci dans kustomization.yaml
images:
  - name: traefik
    newName: traefik
    newTag: v2.11  # Changez la version ici
```

### Changer le namespace

```yaml
# Modifiez dans kustomization.yaml
namespace: traefik-system
```

### Ajouter des ressources supplémentaires

```yaml
# Ajoutez dans la section resources
resources:
  - traefik-rbac.yaml
  - traefik-config.yaml
  - traefik-deployment.yaml
  - traefik-service.yaml
  - mes-ressources-supplementaires.yaml
```

## Nettoyage

Pour supprimer Traefik et ses ressources:

```bash
cd traefik
kubectl delete -k .
```

Ou manuellement:

```bash
cd traefik
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

4. **Voir la configuration générée**:
   ```bash
   kubectl kustomize .
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

- Ce déploiement utilise l'image `traefik:v2.10` par défaut
- Le service est de type LoadBalancer pour un accès local facile
- Les permissions RBAC sont configurées pour permettre à Traefik de découvrir les services et ingress
- Kustomize permet une gestion plus propre et plus flexible des configurations Kubernetes
