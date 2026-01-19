#!/bin/bash

# cleanup.sh
# Script pour nettoyer toutes les ressources du projet SAE503

echo "Nettoyage des ressources du projet SAE503..."

# Vérifier si kubectl est installé
if ! command -v kubectl &> /dev/null; then
    echo "Erreur: kubectl n'est pas installé."
    exit 1
fi

# Supprimer toutes les ressources avec Kustomize
kubectl delete -k .

echo "Attente que les ressources soient supprimées..."
sleep 10

# Supprimer le namespace haddock (optionnel)
read -p "Voulez-vous aussi supprimer le namespace haddock ? (y/n) " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Suppression du namespace haddock..."
    kubectl delete namespace haddock
    echo "Namespace haddock supprimé."
else
    echo ""
    echo "Namespace haddock conservé."
fi

# Vérifier que tout a été supprimé
echo "Ressources restantes dans le namespace haddock:"
kubectl get all -n haddock

echo "Nettoyage terminé!"
