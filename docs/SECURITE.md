# Sécurité - Shida

## Vue d'ensemble

La sécurité est une priorité pour Shida. Ce document décrit les mesures mises en place pour protéger les utilisateurs et leurs données.

## Authentification

### Mots de passe

- Longueur minimum: 6 caractères
- Longueur maximum: 128 caractères
- Hashage: Werkzeug security avec algorithme par défaut (PBKDF2-SHA256)
- Jamais stockés en clair

### Sessions

- Gérées par Flask-Login
- Secret key requis en production
- Cookies HTTPOnly et Secure

### Protection contre les attaques

#### Brute Force

Le rate limiter bloque après 5 tentatives de connexion en 5 minutes. Le blocage dure 15 minutes.

#### Credential Stuffing

- Rate limiting par IP
- Pas de message d'erreur révélant si l'email existe

## Protection des Données

### Validation des entrées

Toutes les entrées utilisateur passent par des fonctions de validation:

#### Email
- Format RFC 5321 vérifié par regex
- Longueur maximum: 254 caractères

#### Mots de passe
- Minimum 6 caractères
- Maximum 128 caractères
- Pas de restriction de complexité (pour l'expérience utilisateur)

#### Données de profil
- Nom: 2-100 caractères, lettres et accents uniquement
- Age: 18-120 ans
- Bio: maximum 1000 caractères
- URL photo: doit commencer par http:// ou https://

### Sanitization XSS

Toutes les entrées texte sont:
1. Échappées HTML (via html.escape)
2. Nettoyées des patterns dangereux:
   - Balises script
   - Handlers JavaScript (onclick, etc.)
   - URLs javascript:
   - Data URIs HTML

### Injection SQL

Protection assurée par:
- Utilisation exclusive de l'ORM SQLAlchemy
- Paramètres préparés pour toutes les requêtes
- Pas de requêtes SQL brutes

## Rate Limiting

Système de limitation des requêtes pour prévenir les abus.

### Limites par action

| Action | Requêtes | Fenêtre | Blocage |
|--------|----------|---------|---------|
| Connexion | 5 | 5 min | 15 min |
| Inscription | 3 | 1 heure | 1 heure |
| Swipe | 100 | 1 heure | 10 min |
| Message | 50 | 1 heure | 10 min |
| Signalement | 10 | 1 heure | 30 min |
| API générale | 200 | 1 min | 5 min |

### Fonctionnement

1. Chaque requête est identifiée par IP + action
2. Les requêtes sont stockées avec timestamp
3. Les anciennes requêtes sont nettoyées automatiquement
4. Dépassement = blocage temporaire

### Reset

- Connexion réussie: reset du compteur login
- Les compteurs expirent naturellement après la fenêtre

## Détection de Fraude

### Analyse des messages

Chaque message est analysé pour détecter:

#### Patterns suspects
- Demandes d'argent ("envoie de l'argent", "western union", etc.)
- Services de transfert (MoneyGram, etc.)
- Références bancaires (numéro de compte, carte de crédit)
- Cryptomonnaies
- Mots d'arnaque (héritage, loterie, gagnant)
- Urgence artificielle
- Contact externe (WhatsApp, Telegram, numéros de téléphone)

#### Comportement

- Messages en majuscules
- Excès de ponctuation
- Messages très longs
- Messages répétitifs identiques
- Volume anormal de messages par heure

### Scoring

Chaque indicateur ajoute des points au score de suspicion:

| Score | Action |
|-------|--------|
| 0-29 | Autorisé |
| 30-49 | Message flagué pour modération |
| 50+ | Message bloqué |

### Analyse comportementale

Surveillance des comportements utilisateur:

#### Indicateurs surveillés
- Likes envoyés par jour (normal: <100, suspect: >200)
- Messages envoyés par jour (normal: <50, suspect: >100)
- Signalements reçus récemment
- Activité anormale des nouveaux comptes

#### Actions automatiques

| Score | Recommandation |
|-------|----------------|
| 0-29 | Aucune action |
| 30-49 | Surveillance |
| 50-79 | Revue manuelle requise |
| 80+ | Ban automatique |

### Analyse de profil

Vérification des profils suspects:
- Absence de photo (+10 points)
- Bio manquante ou trop courte (+5 à +10 points)
- Patterns suspects dans la bio (+15 points)
- Age invalide (+30 points)

## Signalement Utilisateur

### Types de signalement

1. **Contenu inapproprié**: Photos ou textes choquants
2. **Harcèlement**: Comportement insistant ou menaçant
3. **Faux profil**: Identité usurpée ou inventée
4. **Spam**: Messages publicitaires répétitifs
5. **Arnaque**: Tentative d'escroquerie
6. **Mineur**: Personne semblant avoir moins de 18 ans
7. **Autre**: Cas non couverts

### Traitement

1. Signalement enregistré avec détails
2. Priorité automatique si type "mineur"
3. Revue par modérateur
4. Action: Avertissement, Ban, ou Rejet du signalement
5. Notification au signalant (optionnel)

## Administration Sécurisée

### Authentification admin

- Système séparé de l'auth utilisateur
- Sessions distinctes
- Pas de lien entre comptes admin et utilisateur

### Permissions

Modèle de rôles:
- **super_admin**: Accès complet
- **moderator**: Modération uniquement
- **manager**: Gestion commerciale

Vérification des permissions sur chaque route admin.

### Audit

Toutes les actions admin sont tracées:
- Identité de l'admin
- Action réalisée
- Cible (utilisateur, signalement, etc.)
- Timestamp
- Adresse IP

Les logs sont consultables par les super admins.

## Sécurité Infrastructure

### Proxy et HTTPS

- ProxyFix middleware pour détecter HTTPS
- Headers de sécurité via ProxyFix
- URLs générées en HTTPS grâce à ProxyFix

### Cache

- Headers no-cache sur toutes les réponses
- Évite les données sensibles en cache

### Base de données

- Connexions PostgreSQL sécurisées
- Pool de connexions avec recyclage (300s)
- Pre-ping pour vérifier la validité des connexions

### Variables d'environnement

Données sensibles stockées en variables:
- `DATABASE_URL`: Connexion BDD
- `SESSION_SECRET`: Clé de session

Jamais codées en dur dans le code source.

## Recommandations de Déploiement

### Production

1. Définir un SECRET_KEY fort et unique
2. Utiliser HTTPS obligatoire
3. Configurer des backups réguliers de la BDD
4. Monitorer les logs d'erreur
5. Mettre à jour les dépendances régulièrement

### Mots de passe admin

1. Changer le mot de passe admin par défaut immédiatement
2. Utiliser des mots de passe forts (12+ caractères)
3. Activer l'authentification à deux facteurs si disponible
4. Rotation régulière des accès

### Monitoring

Surveiller:
- Tentatives de connexion échouées
- Pics de signalements
- Comportements anormaux détectés
- Bans automatiques

## Conformité RGPD

### Données collectées

- Email (obligatoire)
- Informations de profil (volontaires)
- Historique de matchs et messages
- Logs de connexion

### Droits utilisateur

- Accès: Possibilité de consulter ses données
- Rectification: Modification du profil
- Suppression: Suppression de compte disponible
- Portabilité: Export des données (à implémenter)

### Conservation

- Données utilisateur: Jusqu'à suppression du compte
- Logs de sécurité: 1 an
- Messages: Jusqu'à suppression du match

### Mentions légales

Pages de contenu disponibles:
- Conditions d'utilisation
- Politique de confidentialité

Accessibles via `/page/{slug}`.

## Plan de Réponse aux Incidents

### Détection

1. Alertes sur comportements anormaux
2. Monitoring des logs
3. Signalements utilisateurs

### Réponse

1. Identifier la nature de l'incident
2. Isoler les comptes compromis
3. Collecter les preuves
4. Corriger la faille
5. Notifier les utilisateurs affectés

### Communication

- Transparence envers les utilisateurs affectés
- Documentation interne de l'incident
- Amélioration des mesures préventives

## Checklist Sécurité

### Avant mise en production

- [ ] SESSION_SECRET défini et unique
- [ ] Mot de passe admin changé
- [ ] HTTPS configuré
- [ ] Backups automatiques
- [ ] Logs accessibles
- [ ] Rate limiting testé
- [ ] Validation des entrées testée

### Maintenance régulière

- [ ] Revue des logs d'audit
- [ ] Mise à jour des dépendances
- [ ] Test de restauration backup
- [ ] Revue des signalements non traités
- [ ] Vérification des bans automatiques
