#!/bin/bash

# fix-namespace-simple.sh
# Script simplifié pour corriger les problèmes de namespace (sans dépendance jq)

echo "Correction des problèmes de namespace haddock..."

# Vérifier si kubectl est installé
if ! command -v kubectl &> /dev/null; then
    echo "Erreur: kubectl n'est pas installé."
    exit 1
fi

# Vérifier l'état du namespace
echo "Vérification du namespace haddock..."
NAMESPACE_STATUS=$(kubectl get namespace haddock -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")

echo "État du namespace: $NAMESPACE_STATUS"

# Si le namespace est en cours de suppression
if [ "$NAMESPACE_STATUS" = "Terminating" ]; then
    echo "Le namespace haddock est en cours de suppression..."
    
    # Méthode 1: Essayer une suppression normale avec grace period 0
    echo "Tentative de suppression avec grace-period=0..."
    kubectl delete namespace haddock --grace-period=0 --force
    
    # Attendre la suppression
    echo "Attente de la suppression complète..."
    for i in {1..10}; do
        if ! kubectl get namespace haddock &> /dev/null; then
            echo "Namespace supprimé avec succès!"
            break
        fi
        sleep 5
        echo "Attente... ($i/10)"
    done
    
    # Si toujours présent après 50 secondes, essayer une autre méthode
    if kubectl get namespace haddock &> /dev/null; then
        echo "Le namespace résiste, essayons une approche différente..."
        echo "Vous devrez peut-être supprimer manuellement les ressources bloquantes."
        echo "Ressources dans le namespace:"
        kubectl api-resources --verbs=list --namespaced=true -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n haddock
    fi
fi

# Recréer le namespace s'il n'existe pas
if ! kubectl get namespace haddock &> /dev/null; then
    echo "Création du namespace haddock..."
    kubectl create namespace haddock
    echo "Namespace haddock créé avec succès!"
else
    echo "Le namespace haddock existe déjà."
fi

# Vérifier que le namespace est prêt
echo "Vérification du namespace haddock:"
kubectl get namespace haddock

echo ""
echo "Si le namespace est toujours bloqué, vous pouvez essayer:"
echo "1. kubectl delete namespace haddock --grace-period=0 --force"
echo "2. Attendre quelques minutes et réessayer"
echo "3. Vérifier les ressources bloquantes avec: kubectl get all -n haddock"
