### **Lot 1 : Définition de l’architecture**
**Livrable** : Un **dossier d’architecture technique (DAT)**.
**Tâches** :
- Rédiger un document détaillant :
  - L’architecture globale (conteneurs, orchestrateur, stockage, réseau).
  - Les choix techniques (Kubernetes, Traefik, stockage persistant, etc.).
  - Les diagrammes (architecture, flux réseau, etc.).
  - Les justifications des choix (ex : pourquoi Kubernetes ? Pourquoi Traefik ?).

---

### **Lot 2 : Mise en place et configuration d’un orchestrateur de conteneurs**
**Livrable** : Un **cahier d’installation technique (CIT)**.
**Tâches** :
- Installer et configurer un orchestrateur (ex : **Kubernetes** ou **Docker Swarm**) sur une VM.
- Documenter :
  - L’architecture matérielle/logicielle.
  - L’adressage réseau et la matrice de flux.
  - Les schémas de principe.
  - Les commandes et fichiers de configuration utilisés.

---

### **Lot 3 : Refactorisation de l’application**
**Livrable** : Un **repository Git** contenant :
- Le code refactorisé en **3 microservices** :
  1. Gestion des utilisateurs (`/users`).
  2. Gestion des citations (`/quotes`).
  3. Recherche de citations (`/search`).
- Un **Dockerfile** pour chaque microservice.
**Tâches** :
- Adapter le code pour respecter les **12-Factor App** (ex : variables d’environnement, stateless).
- Créer un Dockerfile pour chaque microservice.
- *(Bonus)* : Modifier l’authentification pour utiliser les identifiants/mots de passe de la base de données.

---

### **Lot 4 : Instanciation de l’application dans l’orchestrateur**
**Livrable** : Les **manifestes de déploiement** dans un repository Git.
**Tâches** :
- Déployer l’application sur Kubernetes/Docker Swarm :
  - Créer des **manifestes** (Deployment, Service, Ingress, etc.).
  - Configurer un **reverse proxy** (Traefik) pour router les requêtes.
  - Utiliser **nip.io** pour créer des FQDN.
  - *(Bonus)* : Créer un **chart Helm** pour le déploiement.

---

### **Lot 5 : Sécurité**
**Livrable** : Un fichier **SECURITY.md** (voir modèle précédent).
**Tâches** :
- Appliquer les exigences de sécurité :
  - Stockage des secrets dans **Kubernetes Secrets**.
  - Isolation des environnements via des **namespaces**.
  - Utilisation d’**images Docker minimales** et configuration du **SecurityContext**.
  - Limitation des requêtes HTTP (10/min) via Traefik.
  - Scanner les images avec **Trivy**.
- Documenter les preuves et les limites.

---

### **Tâches transverses**
- **Gestion du projet** :
  - S’enregistrer sur **Github Classrooms** ([lien](https://bit.ly/iutsm-sae503)).
  - Taguer les livrables finaux avec « **sae503** » avant le **02 février 2026 à 12h00**.
- **Soutenance** :
  - Préparer une présentation pour expliquer les choix techniques et les résultats.

