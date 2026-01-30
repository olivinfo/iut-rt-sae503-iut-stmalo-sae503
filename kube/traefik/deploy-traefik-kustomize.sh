#!/bin/bash

# deploy-traefik-kustomize.sh
# Script pour déployer Traefik en local en utilisant Kustomize

echo "Déploiement de Traefik en local avec Kustomize..."

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

# Vérifier si kustomize est disponible
if ! kubectl kustomize . &> /dev/null; then
    echo "Erreur: Kustomize n'est pas disponible ou la configuration est invalide."
    exit 1
fi

echo "Déploiement avec Kustomize..."

# Appliquer la configuration Kustomize
kubectl apply -k .

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

# Afficher la configuration appliquée
echo ""
echo "Configuration Kustomize appliquée:"
kubectl kustomize .
