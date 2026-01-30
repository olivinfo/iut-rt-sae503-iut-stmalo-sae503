#!/bin/bash

# deploy-traefik.sh
# Script pour déployer Traefik en local

echo "Déploiement de Traefik en local..."

# Vérifier si kubectl est installé
if ! command -v kubectl &> /dev/null; then
    echo "Erreur: kubectl n'est pas installé. Veuillez installer kubectl et configurer votre cluster Kubernetes."
    exit 1
fi

# Vérifier la connexion au cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "Erreur: Impossible de se connecter au cluster Kubernetes. Veuillez vérifier votre configuration."
    exit 1
fi

echo "Connexion au cluster Kubernetes vérifiée."

# Créer la configuration RBAC
echo "Création de la configuration RBAC..."
kubectl apply -f traefik-rbac.yaml

# Créer la configuration Traefik
echo "Création de la configuration Traefik..."
kubectl apply -f traefik-config.yaml

# Déployer Traefik
echo "Déploiement de Traefik..."
kubectl apply -f traefik-deployment.yaml

# Créer le service Traefik
echo "Création du service Traefik..."
kubectl apply -f traefik-service.yaml

echo "Attente que Traefik soit prêt..."
kubectl wait --for=condition=available --timeout=300s deployment/traefik

echo "Traefik déployé avec succès!"

# Afficher les informations de connexion
echo ""
echo "Informations de connexion:"
echo "- Tableau de bord Traefik: http://localhost:8080"
echo "- Service Traefik: http://localhost:80"
echo ""

# Afficher les ressources créées
echo "Ressources créées:"
kubectl get all -l app=traefik
