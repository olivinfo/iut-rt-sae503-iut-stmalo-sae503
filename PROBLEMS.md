# Problèmes rencontrés et solutions

Ce document recense les défis techniques rencontrés lors du développement de l'application de gestion de citations, ainsi que les solutions mises en œuvre.

## Intégration de Redis

**Problème** : L'import initial des données depuis des fichiers CSV vers Redis posait des défis, notamment pour la gestion des IDs et la structure des données.

**Solution** : Implémentation d'un mécanisme de chargement initial dans chaque service qui vérifie l'existence des données avant de les importer depuis les fichiers CSV. Utilisation de Redis Sets pour gérer les collections et de Redis Hashes pour les objets individuels.

## Architecture microservices

**Problème** : La segmentation de l'application monolithique initiale en trois services distincts (utilisateurs, citations, recherche) nécessitait une refonte complète de l'architecture.

**Solution** :

- Création de trois services indépendants avec des responsabilités claires :
  - Service utilisateurs (port 5000) : gestion des comptes utilisateurs
  - Service citations (port 5001) : gestion des citations (CRUD)
  - Service recherche (port 5002) : fonctionnalités de recherche
- Mise en place d'un système d'authentification cohérent entre les services
- Configuration Docker pour l'orchestration des conteneurs

## Gestion des images Docker

**Problème** : La gestion et le stockage des images Docker pour le déploiement nécessitaient une solution centralisée et versionnée.

**Solution** :

- Utilisation de Docker Hub comme registre d'images
- Mise en place d'un système de versionnage des images (tags)
- Création de Dockerfiles spécifiques pour chaque service
- Configuration de docker-compose pour l'environnement de développement

## Stratégie de branchement Git

**Problème** : La coordination du travail d'équipe nécessitait une stratégie de branchement claire pour éviter les conflits et faciliter l'intégration continue.

**Solution** :

- Adoption d'une stratégie de branchement basée sur les fonctionnalités
- Création de branches dédiées pour chaque fonctionnalité majeure
- Utilisation de pull requests pour la revue de code et l'intégration
- Branche main protégée pour le code stable

## Système d'authentification

**Problème** : La mise en place d'un système d'authentification sécurisé et cohérent entre les trois services indépendants.

**Solution** :

- Implémentation d'un mécanisme d'authentification basé sur une clé API (ADMIN_KEY)
- Transmission du token via l'en-tête HTTP Authorization
- Décorateur @require_auth pour protéger les endpoints sensibles
- Validation indépendante du token par chaque service
- Configuration centralisée via variables d'environnement

## Déploiement Kubernetes

**Problème** : La configuration Kubernetes initiale ne couvrait pas les services de citations, seulement un service de démonstration (whoami).

**Solution en cours** :

- Configuration Traefik comme ingress controller
- Création de fichiers de configuration pour chaque service (Deployment, Service, Ingress)
- Configuration des routes pour exposer les endpoints via Traefik
- Gestion des variables d'environnement via ConfigMaps et Secrets
- Scalabilité horizontale des pods

## Améliorations futures

**Points à améliorer** :

- Remplacement de la clé d'authentification statique par un système JWT
- Implémentation d'un service d'authentification centralisé
- Ajout de tests d'intégration complets
- Documentation API avec Swagger/OpenAPI
- Monitoring et logging centralisés
- Configuration CI/CD pour les déploiements automatiques
