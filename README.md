# Shida - Application de Rencontres

Shida est une application de rencontres moderne conçue pour la communauté congolaise. Le nom "Shida" signifie "problème" en lingala, et notre slogan "Zala na Temps" signifie "Prends ton temps" - encourageant les utilisateurs à construire des relations authentiques.

## Fonctionnalités

### Pour les utilisateurs
- **Découverte de profils** - Explorez des profils compatibles avec un système de swipe intuitif
- **Matching intelligent** - Algorithme de compatibilité basé sur la religion, localisation, objectifs et intérêts
- **Messagerie** - Discutez avec vos matchs de manière sécurisée
- **Système de jetons** - Économie in-app pour débloquer des fonctionnalités premium
- **Mode Fantôme** - Naviguez incognito (fonctionnalité VIP)
- **Vérification de profil** - Badge de confiance pour les profils vérifiés

### Pour les administrateurs
- Dashboard d'analytics complet
- Gestion des utilisateurs et modération
- Configuration des plans tarifaires
- Système de tickets support
- Logs d'audit détaillés

## Stack Technique

- **Backend**: Flask (Python)
- **Base de données**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentification**: Flask-Login
- **Frontend**: HTML/CSS/JavaScript avec TailwindCSS
- **Serveur**: Gunicorn

## Installation

1. Clonez le repository
2. Installez les dépendances: `pip install -r requirements.txt`
3. Configurez les variables d'environnement:
   - `DATABASE_URL` - URL de connexion PostgreSQL
   - `SESSION_SECRET` - Clé secrète pour les sessions
4. Lancez l'application: `gunicorn --bind 0.0.0.0:5000 main:app`

## Structure du Projet

```
├── app.py              # Configuration Flask principale
├── main.py             # Point d'entrée
├── models/             # Modèles SQLAlchemy
├── routes/             # Blueprints Flask (API, vues, admin)
├── services/           # Logique métier
├── security/           # Validation et sécurité
├── templates/          # Templates Jinja2
├── statics/            # CSS et JavaScript
└── data/               # Données de seed
```

## API Principales

- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/discovery` - Profils à découvrir
- `POST /api/discovery/swipe` - Swipe sur un profil
- `GET /api/matches` - Liste des matchs
- `GET/POST /api/matches/<id>/messages` - Messages d'un match

## Licence

Projet propriétaire - Tous droits réservés.
