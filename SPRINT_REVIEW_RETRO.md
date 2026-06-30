# Compte-rendu Sprint Review & Rétrospective — SmartBacklog

**Projet :** SmartBacklog  
**Équipe :** Donbeni (PO), Phanuel (SM), Rolince (Dev), HK (Dev)  
**GitHub :** https://github.com/Donblack12/smartbacklog

---

## Sprint 1 — Review

**Période :** Mars 2026  
**Objectif :** Livrer le MVP — tableau Kanban fonctionnel avec authentification

### Ce qui a été livré

**Phanuel — Frontend**
- Page de connexion et d'inscription avec validation des champs
- Tableau Kanban avec 3 colonnes : To Do / In Progress / Done
- Interface responsive et intuitive en HTML/CSS/JS pur

**Rolince — Backend**
- API REST complète avec Flask (Python)
- Routes d'authentification : inscription et connexion sécurisées (hash SHA-256)
- Routes CRUD pour les tickets : créer, lire, modifier, supprimer
- Persistance des données avec SQLite

**Donbeni — Coordination**
- Définition du Product Backlog et des User Stories
- Structure du projet et documentation README
- Coordination entre les membres de l'équipe

### Démonstration Sprint 1
L'application permettait à la fin du Sprint 1 de :
- Créer un compte et se connecter
- Créer des tickets et les déplacer entre les colonnes
- Supprimer des tickets
- Conserver les données entre les sessions grâce à SQLite

---

## Sprint 1 — Rétrospective

### Ce qui a bien fonctionné
- Bonne répartition des tâches entre frontend, backend et coordination
- Communication fluide au sein de l'équipe
- Livraison du MVP dans les délais prévus

### Ce qui peut être amélioré
- Mieux documenter les endpoints de l'API pour faciliter l'intégration IA au Sprint 2
- Ajouter la validation des données côté backend dès le départ
- Planifier les tests plus tôt dans le sprint

### Actions décidées pour le Sprint 2
- Rolince : renforcer la sécurité du backend (token de session, validation renforcée)
- Phanuel : améliorer l'UX (drag & drop, filtres, dark mode)
- HK : prendre en charge l'intégration de l'API OpenAI
- Donbeni : préparer le Product Backlog Sprint 2 et suivre l'avancement

---

## Sprint 2 — Review

**Période :** Avril — Mai 2026  
**Objectif :** Intégrer l'IA pour enrichir automatiquement les tickets

### Ce qui a été livré

**HK — Intégration IA**
- Connexion à l'API OpenAI (GPT-4o)
- Implémentation du Prompt Engineering : system prompt "Coach Agile expert"
- Génération automatique de 3 à 5 critères d'acceptation par ticket
- Estimation de la complexité en Story Points (suite de Fibonacci : 1, 2, 3, 5, 8, 13)
- Analyse de priorité automatique : urgent / bloquant / normal

**Phanuel — Améliorations Frontend**
- Drag & drop entre les colonnes du Kanban
- Barre de filtres (statut, priorité, recherche par mot-clé)
- Modal d'édition complète d'un ticket
- Mode sombre / mode clair
- Export des tickets en CSV
- Badges de dates d'échéance (vert / orange / rouge)

**Rolince — Renforcement Backend**
- Token de session UUID pour l'authentification
- Route de déconnexion côté serveur
- Validation renforcée des données (longueur max, types)
- Route de statistiques `/stats`
- Filtres côté serveur (recherche texte, statut, priorité)

### Démonstration Sprint 2
L'application permet désormais de :
- Cliquer sur "Analyser IA" sur n'importe quel ticket
- Obtenir en 3-5 secondes des critères d'acceptation générés par GPT-4o
- Voir les Story Points et la priorité suggérés automatiquement
- Bénéficier de toutes les améliorations UX du Sprint 2

---

## Sprint 2 — Rétrospective

### Ce qui a bien fonctionné
- L'intégration IA s'est faite sans impacter le code existant
- La séparation claire des responsabilités entre les membres a facilité le travail en parallèle
- Le Prompt Engineering a donné des résultats de haute qualité dès le premier essai

### Ce qui peut être amélioré
- Anticiper plus tôt la question de la clé API (coût, gestion des secrets)
- Prévoir des tests automatisés pour la route IA
- Mieux gérer les erreurs réseau côté frontend

### Bilan général
Le projet SmartBacklog répond à l'ensemble du cahier des charges :
- Tableau Kanban complet avec CRUD ✅
- Authentification sécurisée ✅
- Intégration IA avec Prompt Engineering ✅
- Collaboration sur GitHub avec 4 contributeurs ✅
- 17 User Stories livrées pour 55 Story Points au total ✅
