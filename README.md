# SmartBacklog

Assistant intelligent pour la gestion de produits Agile avec IA intégrée.

## Équipe
| Membre | Rôle Agile | Rôle Tech |
|--------|-----------|-----------|
| Donbeni | Product Owner | Dev — README + coordination |
| Phanuel | Scrum Master | Dev — Frontend |
| Rolince | Developer | Dev — Backend Flask |
| HK | Developer | Dev — Intégration IA |

## Stack technique
- Frontend : HTML + CSS + JavaScript vanilla
- Backend : Python Flask
- IA : API Anthropic Claude (Sprint 2)

## Structure du projet
```
smartbacklog/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   └── index.html
└── README.md
```

## Lancer le projet

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Frontend
Ouvrir `frontend/index.html` dans le navigateur.

## Fonctionnalités

### Sprint 1 — MVP
- Inscription et connexion sécurisée
- Tableau Kanban avec 3 colonnes (A faire / En cours / Terminé)
- Créer, déplacer et supprimer des tickets

### Sprint 2 — IA
- Génération automatique des critères d'acceptation
- Estimation des Story Points via IA
- Analyse de priorité des tickets

## GitHub
https://github.com/Donblack12/smartbacklog