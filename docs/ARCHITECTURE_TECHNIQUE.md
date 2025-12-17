# Architecture Technique - Shida

## Vue d'ensemble

Shida est une application de rencontre construite avec Flask (Python). L'application suit une architecture MVC (Modèle-Vue-Contrôleur) avec une séparation claire des responsabilités.

## Stack Technologique

### Backend
- **Framework**: Flask 
- **Base de données**: PostgreSQL
- **ORM**: SQLAlchemy via Flask-SQLAlchemy
- **Authentification**: Flask-Login
- **Serveur WSGI**: Gunicorn

### Frontend
- **Templating**: Jinja2
- **CSS**: Tailwind CSS (CDN)
- **JavaScript**: Vanilla JS
- **Icônes**: Feather Icons

## Structure des Dossiers

```
/
├── app.py              # Point d'entrée, configuration Flask
├── main.py             # Module d'import pour Gunicorn
├── models/             # Modèles de données SQLAlchemy
│   ├── __init__.py     # Export des modèles
│   ├── base.py         # Instance SQLAlchemy
│   ├── auth.py         # User, AdminUser
│   ├── social.py       # Profile, Like, Match, Message
│   ├── commerce.py     # Subscription, TokenTransaction, PricingPlan, PromoCode
│   ├── content.py      # Notification, ContentPage, MatchingConfig
│   └── admin.py        # Report, AuditLog, SupportTicket, TicketResponse
├── routes/             # Contrôleurs (Blueprints Flask)
│   ├── views.py        # Routes frontend (pages HTML)
│   ├── api.py          # API REST JSON
│   └── admin.py        # Interface admin
├── services/           # Logique métier
│   ├── match_service.py
│   ├── subscription_service.py
│   ├── token_service.py
│   ├── notification_service.py
│   ├── gamification_service.py
│   ├── verification_service.py
│   └── report_service.py
├── security/           # Sécurité et validation
│   ├── validators.py
│   ├── fraud_detection.py
│   ├── rate_limiter.py
│   └── decorators.py
├── templates/          # Templates Jinja2
│   ├── base.html
│   ├── app/            # Pages utilisateur
│   ├── auth/           # Connexion/Inscription
│   ├── admin/          # Interface admin
│   └── components/     # Composants réutilisables
├── statics/            # Fichiers statiques
│   ├── css/
│   └── js/
└── data/               # Données de configuration
    ├── init_db.py      # Initialisation base de données
    └── gamification.json
```

## Modèles de Données

### User (models/auth.py)
Table principale des utilisateurs.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| email | String(120) | Email unique |
| password_hash | String(256) | Mot de passe hashé |
| is_vip | Boolean | Statut VIP |
| vip_type | String(20) | Type VIP (free, Gold, Platinum) |
| vip_expires_at | DateTime | Expiration VIP |
| tokens | Integer | Solde de jetons |
| ghost_mode | Boolean | Mode fantôme (VIP) |
| is_active | Boolean | Compte actif |
| is_banned | Boolean | Compte banni |
| ban_reason | Text | Raison du bannissement |

### Profile (models/social.py)
Profil public de l'utilisateur.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| user_id | Integer | FK vers User |
| name | String(100) | Nom affiché |
| age | Integer | Age |
| bio | Text | Bio personnelle |
| photo_url | String(500) | Photo principale |
| religion | String(50) | Religion |
| tribe | String(50) | Tribu/Origine |
| profession | String(100) | Profession |
| objective | String(50) | Objectif (Mariage, Amitié, etc.) |
| location | String(100) | Localisation |
| views_count | Integer | Nombre de vues |
| is_verified | Boolean | Profil vérifié |

### Match (models/social.py)
Représente un match entre deux utilisateurs.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| user1_id | Integer | Premier utilisateur |
| user2_id | Integer | Second utilisateur |
| compatibility_score | Float | Score de compatibilité |
| is_active | Boolean | Match actif |

### Subscription (models/commerce.py)
Abonnements VIP des utilisateurs.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| user_id | Integer | FK vers User |
| plan_type | String(50) | Type d'abonnement |
| price | Float | Prix payé |
| status | String(20) | Statut (active, expired, cancelled) |
| starts_at | DateTime | Début |
| expires_at | DateTime | Fin |
| auto_renew | Boolean | Renouvellement auto |

## Services

### MatchService
Gestion du matching et de la découverte.

**Fonctions principales:**
- `calculate_compatibility(profile1, profile2)`: Calcule le score de compatibilité basé sur les poids configurés (religion, localisation, objectif, profession, age, intérêts)
- `get_discovery_profiles(user, limit)`: Retourne les profils à afficher, triés par compatibilité
- `process_like(sender, receiver_id)`: Traite un like et crée un match si mutuel
- `get_user_matches(user)`: Liste les matchs d'un utilisateur

### SubscriptionService
Gestion des abonnements VIP.

**Fonctions principales:**
- `subscribe(user, plan_id)`: Souscrit un abonnement
- `cancel_subscription(user)`: Annule le renouvellement
- `check_expiring_subscriptions()`: Notifie les abonnements qui expirent bientôt
- `process_expired_subscriptions()`: Marque les abonnements expirés

### TokenService
Gestion des jetons virtuels.

**Coûts des actions:**
- Saluer un match: 1 jeton
- Super like: 3 jetons
- Boost de profil: 5 jetons
- Voir les likes: 2 jetons
- Annuler un swipe: 1 jeton

**Fonctions principales:**
- `use_tokens(user, action)`: Consomme des jetons
- `add_tokens(user, amount)`: Ajoute des jetons
- `apply_promo_code(user, code)`: Applique un code promo

### GamificationService
Système de badges, niveaux et achievements.

**Badges disponibles:**
- Profil Vérifié
- VIP Gold / VIP Platinum
- Populaire (100+ vues)
- Maître des Matchs (10+ matchs)
- Profil Complet

**Niveaux:**
1. Nouveau (0 XP)
2. Actif (100 XP)
3. Régulier (300 XP)
4. Populaire (600 XP)
5. Star (1000 XP)
6. Légende (2000 XP)

## Sécurité

### Rate Limiting (security/rate_limiter.py)
Limite les requêtes par action:

| Action | Limite | Fenêtre | Blocage |
|--------|--------|---------|---------|
| login | 5 | 5 min | 15 min |
| register | 3 | 1 heure | 1 heure |
| swipe | 100 | 1 heure | 10 min |
| message | 50 | 1 heure | 10 min |
| report | 10 | 1 heure | 30 min |

### Détection de Fraude (security/fraud_detection.py)
Analyse les messages et comportements suspects:

**Patterns surveillés:**
- Demandes d'argent
- Références à des services de transfert (Western Union, etc.)
- Numéros de téléphone
- Liens vers messageries externes (WhatsApp, Telegram)
- Mots-clés financiers (bitcoin, héritage, loterie)

**Analyse comportementale:**
- Volume de likes/messages envoyés
- Messages répétitifs
- Signalements reçus
- Activité anormale des nouveaux comptes

### Validation des Entrées (security/validators.py)
- Validation d'email (format, longueur)
- Validation de mot de passe (min 6 caractères)
- Sanitization XSS (échappement HTML, suppression de scripts)
- Validation des données de profil

## API REST

Toutes les routes API sont préfixées par `/api`.

### Authentification
- `POST /api/auth/register`: Inscription
- `POST /api/auth/login`: Connexion
- `POST /api/auth/logout`: Déconnexion
- `GET /api/auth/me`: Utilisateur courant

### Profil
- `GET /api/profile`: Lire le profil
- `PUT /api/profile`: Modifier le profil
- `POST /api/profile/ghost-mode`: Toggle mode fantôme (VIP)
- `POST /api/profile/verification`: Soumettre vérification

### Découverte et Matchs
- `GET /api/discovery`: Profils à découvrir
- `POST /api/discovery/swipe`: Like/Pass
- `GET /api/matches`: Liste des matchs
- `GET /api/matches/<id>/messages`: Messages d'un match
- `POST /api/matches/<id>/messages`: Envoyer un message

### Commerce
- `GET /api/market/plans`: Plans disponibles
- `POST /api/market/purchase`: Acheter un plan
- `POST /api/market/promo`: Appliquer code promo
- `GET /api/subscription`: Abonnement actuel
- `POST /api/subscription/cancel`: Annuler

### Gamification
- `GET /api/dashboard/stats`: Statistiques
- `GET /api/gamification/badges`: Badges
- `GET /api/gamification/achievements`: Achievements
- `GET /api/gamification/level`: Niveau

## Interface Admin

Accessible via `/admin`. Système séparé de l'authentification utilisateur avec sessions distinctes.

### Rôles
- **super_admin**: Accès complet
- **moderator**: Modération et support
- **manager**: Gestion commerciale

### Fonctionnalités
- Dashboard avec statistiques temps réel
- Gestion des utilisateurs (ban, vérification, ajout tokens, VIP)
- Modération des signalements
- Configuration de l'algorithme de matching
- Gestion des plans tarifaires et codes promo
- Envoi de notifications en masse
- Gestion du contenu (pages légales)
- Logs d'audit

## Configuration du Matching

L'algorithme de compatibilité utilise des poids configurables:

| Critère | Poids par défaut |
|---------|------------------|
| Objectif | 30% |
| Religion | 20% |
| Localisation | 15% |
| Age | 15% |
| Profession | 10% |
| Intérêts | 10% |

Les poids sont modifiables via l'interface admin.

## Base de Données

### Configuration
- PostgreSQL hébergé
- Pool de connexions avec recyclage (300s)
- Pre-ping pour vérification de connexion

### Migrations
Les tables sont créées automatiquement via `db.create_all()` au démarrage. Pour les modifications de schéma en production, utiliser Flask-Migrate ou des scripts SQL manuels.

## Déploiement

### Variables d'environnement requises
- `DATABASE_URL`: URL PostgreSQL
- `SESSION_SECRET`: Clé secrète pour les sessions

### Commande de démarrage
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Points d'attention

1. **Cache désactivé**: Headers no-cache sur toutes les réponses pour éviter les problèmes dans l'iframe Replit
2. **ProxyFix**: Middleware pour gérer HTTPS derrière un reverse proxy
3. **Initialisation DB**: Le script `init_db.py` crée des données de démo au premier démarrage
