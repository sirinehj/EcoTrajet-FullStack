# EcoTrajet - Plateforme de Transport

## 📋 Présentation

EcoTrajet est une plateforme innovante de transport collaboratif qui permet aux utilisateurs de créer et participer à des communautés locales pour optimiser leurs déplacements quotidiens. Notre solution vise à faciliter le covoiturage et à créer des liens sociaux autour de la mobilité durable.

## 🚀 Fonctionnalités Principales

### 👥 Gestion des Utilisateurs
- Inscription et connexion sécurisée
- Gestion des rôles (conducteur/passager)
- Profils personnalisés avec préférences de trajet
- Gestion des véhicules

### 🌍 Système de Communautés
- Création et gestion de communautés thématiques
- Administration des membres
- Filtrage par zone géographique

### 🚗 Gestion des Trajets
- Publication de trajets avec détails complets
- Système de réservation en temps réel
- Recherche avancée par communauté
- Gestion des places disponibles

### ⭐ Système d'Évaluation
- Notation après chaque trajet
- Historique des évaluations
- Commentaires et retours d'expérience

### 🔔 Notifications
- Alertes pour nouveaux trajets
- Rappels de réservations
- Notifications de communauté

## 🏗 Architecture du Projet

### Structure des Dossiers
```
EcoTrajet/
├── **backend/** (Django + DRF)
│   ├── EcoTrajet/               # Main Django project
│   │   ├── settings.py          # Global settings
│   │   ├── urls.py              # Root URL routing
│   │   └── ...
│   │
│   ├── **api/**                 # Core API logic
│   │   ├── models/              # Shared models (e.g., Travel, Routes)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── **user_management/**     # Auth & user handling
│       ├── models.py            # Custom User model
│       ├── serializers.py       # Auth serializers
│       ├── views.py             # Login/Register/Profile
│       ├── urls.py              # auth/ routes
│       └── tests/
│
└── **frontend/** (React)
    ├── public/                  # Static files
    ├── src/
    │   ├── **auth/**            # Auth components (Login/Register)
    │   ├── **api/**             # Axios/API calls
    │   ├── **pages/**           # Routes (Dashboard, Profile)
    │   ├── App.js               # Main router
    │   └── ...
    └── package.json
```

## 🛠 Technologies Utilisées

### Backend
- Python 3.8+
- Django/Django REST Framework
- PostgreSQL
- JWT Authentication

### Frontend
- React.js
- Material-UI

### Outils & Infrastructure
- GitHub Actions (CI/CD)

## 📦 Modules & Entités

### Principales Entités
- Utilisateur
- Communauté
- Trajet
- Réservation
- Évaluation
- Notification

## 📝 Prérequis

- Python 3.8 ou supérieur
- Node.js 14 ou supérieur
- PostgreSQL

## ⚡ Démarrage Rapide

1. **Cloner le dépôt**
```bash
git clone https://github.com/sirinehj/EcoTrajet-FullStack.git
cd EcoTrajet-FullStack
```

2. **Configuration de l'environnement**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Créer le fichier .env
cp .env.example .env
```

3. **Configuration de la base de données**
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Lancer l'application**
```bash
# Backend
python manage.py runserver

# Frontend
cd ../frontend
npm install
npm start
```

5. **Accéder à l'application**
- Frontend: http://localhost:3000
- API Backend: http://localhost:8000
- Administration: http://localhost:8000/admin

## 🤝 Contribution

Les contributions sont les bienvenues! Veuillez suivre ces étapes:
1. Forker le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT.
