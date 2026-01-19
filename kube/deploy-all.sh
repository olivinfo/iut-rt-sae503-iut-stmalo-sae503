#!/bin/bash

# deploy-all.sh
# Script pour déployer tout le projet SAE503 avec Kustomize

echo "Déploiement du projet SAE503 avec Kustomize..."

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


if ! kubectl get namespace haddock &> /dev/null; then
    echo "Création du namespace haddock..."
    kubectl create namespace haddock
    if [ $? -ne 0 ]; then
        echo "Erreur: Impossible de créer le namespace haddock."
        exit 1
    fi
else
    echo "Namespace haddock existe déjà et est prêt."
fi

echo "Déploiement de toutes les ressources dans le namespace haddock..."

# Appliquer la configuration Kustomize principale
kubectl apply -k .

echo "Attente que les déploiements soient prêts..."

# Attendre que Traefik soit prêt
kubectl wait --for=condition=available --timeout=300s deployment/traefik

# Attendre que whoami soit prêt
kubectl wait --for=condition=available --timeout=300s deployment/whoami

echo "Projet SAE503 déployé avec succès!"

# Afficher les informations de connexion
echo ""
echo "Informations de connexion:"
echo "- Tableau de bord Traefik: http://localhost:8080"
echo "- Service Traefik: http://localhost:80"
echo "- Service Whoami: http://localhost:8081 (via NodePort)"
echo ""

# Afficher toutes les ressources créées
echo "Ressources créées:"
kubectl get all --show-labels

# Afficher la configuration Kustomize finale
# echo ""
# echo "Configuration Kustomize appliquée:"
# kubectl kustomize .
