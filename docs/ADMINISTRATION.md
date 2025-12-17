# Guide d'Administration - Shida

## Accès à l'Interface Admin

L'interface d'administration est accessible à l'adresse `/admin`.

### Connexion

Utilisez vos identifiants administrateur (email et mot de passe). Le système est séparé de l'authentification utilisateur standard.

### Compte Admin par défaut

Un compte super admin est créé lors de l'initialisation:
- Email: admin@shida.com
- Mot de passe: admin123

**Changez ce mot de passe immédiatement en production.**

## Rôles et Permissions

### Super Admin

Accès complet à toutes les fonctionnalités:
- Gestion des utilisateurs
- Modération
- Configuration matching
- Gestion tarifaire
- Envoi de notifications
- Gestion du contenu
- Administration des comptes admin
- Logs d'audit

### Moderator

Accès limité à:
- Gestion des utilisateurs (actions de base)
- Modération des signalements
- Gestion des tickets support

### Manager

Accès limité à:
- Tableau de bord
- Statistiques
- Gestion tarifaire
- Codes promo

## Tableau de Bord

### Statistiques Principales

- **Utilisateurs totaux**: Nombre total de comptes
- **Nouveaux aujourd'hui**: Inscriptions du jour
- **Nouveaux cette semaine**: Inscriptions des 7 derniers jours
- **Utilisateurs actifs**: Connexion dans les 7 derniers jours
- **Utilisateurs VIP**: Abonnements actifs
- **Total matchs**: Nombre de matchs créés
- **Matchs aujourd'hui**: Matchs du jour
- **Total messages**: Messages échangés
- **Signalements en attente**: Modération requise
- **Tickets ouverts**: Support à traiter
- **Revenus du mois**: Chiffre d'affaires mensuel
- **Jetons vendus**: Jetons achetés ce mois

### Graphique des Inscriptions

Courbe des 7 derniers jours montrant l'évolution des inscriptions quotidiennes.

### Derniers Utilisateurs

Liste des 5 derniers inscrits avec accès direct à leur fiche.

### Signalements Récents

5 derniers signalements en attente nécessitant une action.

## Gestion des Utilisateurs

### Liste des Utilisateurs

Filtres disponibles:
- **Statut**: Tous, Actifs, Bannis, Inactifs
- **VIP**: Tous, VIP, Non-VIP
- **Recherche**: Par email ou nom de profil

### Fiche Utilisateur

Informations affichées:
- Email et date d'inscription
- Dernière connexion
- Statut VIP et type
- Solde de jetons
- Statut de vérification
- Profil complet

Historique:
- Matchs
- Signalements reçus
- Signalements envoyés
- Transactions de jetons

### Actions Disponibles

| Action | Description |
|--------|-------------|
| Bannir | Suspend le compte avec raison |
| Débannir | Réactive un compte banni |
| Vérifier | Valide manuellement le profil |
| Ajouter jetons | Crédite des jetons bonus |
| Définir VIP | Active un abonnement VIP |
| Retirer VIP | Désactive le statut VIP |

Chaque action est enregistrée dans les logs d'audit.

## Modération

### Types de Signalements

- Contenu inapproprié
- Harcèlement
- Faux profil
- Spam
- Arnaque
- Mineur (priorité haute automatique)
- Autre

### Priorités

- **Normal**: Signalement standard
- **High**: Signalement urgent (mineur, arnaque répétée)

### Traitement d'un Signalement

1. Examiner le détail du signalement
2. Consulter le profil signalé et son historique
3. Vérifier les messages si applicable
4. Choisir une action:
   - **Résolu - Aucune action**: Signalement non fondé
   - **Résolu - Avertissement**: Notification d'avertissement envoyée
   - **Résolu - Ban**: Compte banni
5. Ajouter des notes de résolution

### Escalade

Les signalements peuvent être escaladés en priorité haute pour une attention immédiate.

## Configuration du Matching

### Poids de l'Algorithme

Ajustez l'importance de chaque critère dans le calcul de compatibilité:

| Critère | Défaut | Min | Max |
|---------|--------|-----|-----|
| Objectif | 30% | 0% | 50% |
| Religion | 20% | 0% | 30% |
| Localisation | 15% | 0% | 25% |
| Age | 15% | 0% | 25% |
| Profession | 10% | 0% | 20% |
| Intérêts | 10% | 0% | 20% |

Le total doit faire 100%.

### Statistiques de Matching

- Total des matchs
- Matchs du jour
- Score de compatibilité moyen
- Taux match-to-message (% de matchs ayant généré des échanges)

## Gestion Tarifaire

### Plans d'Abonnement

Champs configurables:
- Nom du plan
- Type (subscription ou tokens)
- Prix
- Devise
- Durée (jours)
- Jetons inclus
- Fonctionnalités (liste JSON)
- Actif/Inactif
- Mis en avant

### Codes Promotionnels

Créer un code promo:
- Code (sera converti en majuscules)
- Type de réduction:
  - Pourcentage
  - Montant fixe
  - Jetons bonus
  - Essai VIP (jours)
- Valeur
- Maximum d'utilisations
- Date de validité

Suivi:
- Nombre d'utilisations actuel
- Statut (actif/inactif)

## Envoi de Notifications

### Ciblage

- **Tous les utilisateurs**: Tous les comptes actifs
- **VIP uniquement**: Abonnés VIP
- **Inactifs**: Non connectés depuis 7 jours
- **Spécifique**: Sélection manuelle d'utilisateurs

### Types de Notification

- general: Information générale
- promo: Offre promotionnelle
- update: Mise à jour de l'application
- warning: Avertissement

### Envoi

Remplir:
1. Titre de la notification
2. Message
3. Type
4. Cible

L'envoi est immédiat et enregistré dans les logs.

## Gestion du Contenu

### Pages de Contenu

Gérez les pages légales et informatives:
- Conditions d'utilisation
- Politique de confidentialité
- À propos
- FAQ
- etc.

Chaque page a:
- Un slug (URL)
- Un titre
- Un contenu (HTML autorisé)
- Un statut de publication

### Éditeur

L'éditeur de contenu supporte le HTML basique. Les pages sont accessibles à `/page/{slug}`.

## Sécurité

### Gestion des Admins

(Super admin uniquement)

- Créer de nouveaux comptes admin
- Définir les rôles et permissions
- Désactiver des comptes
- Réinitialiser des mots de passe

### Logs d'Audit

Toutes les actions admin sont enregistrées:
- Qui (admin)
- Quoi (action)
- Sur quoi (cible)
- Quand (timestamp)
- Depuis où (IP)

Actions tracées:
- Connexion/Déconnexion
- Ban/Unban utilisateur
- Vérification de profil
- Ajout de jetons
- Modification VIP
- Résolution de signalement
- Modification de configuration
- Création de code promo
- Envoi de notification
- Modification de contenu

## Support

### Tickets de Support

Les tickets créés par les utilisateurs apparaissent dans la section Support.

Statuts:
- Open: Nouveau ticket
- In Progress: En cours de traitement
- Closed: Résolu

Chaque ticket conserve l'historique des réponses.

## Bonnes Pratiques

### Modération

1. Traiter les signalements "mineur" en priorité
2. Vérifier l'historique avant de bannir
3. Utiliser les avertissements pour les premiers manquements
4. Documenter les décisions dans les notes

### Sécurité

1. Changer régulièrement les mots de passe admin
2. Limiter le nombre de super admins
3. Consulter régulièrement les logs d'audit
4. Désactiver les comptes admin inutilisés

### Performance

1. Surveiller les métriques quotidiennes
2. Identifier les tendances (baisse d'inscriptions, hausse de signalements)
3. Ajuster les paramètres de matching selon les retours
4. Planifier les campagnes promo sur les périodes creuses

## Résolution de Problèmes

### Utilisateur ne peut pas se connecter

1. Vérifier si le compte est banni
2. Vérifier si le compte est actif
3. Proposer une réinitialisation de mot de passe

### Signalement abusif

1. Examiner l'historique du signalant
2. Si signalements répétés non fondés, avertir le signalant
3. Documenter le cas

### Fraude détectée

1. Bannir le compte immédiatement
2. Vérifier les matchs/conversations pour alerter les victimes potentielles
3. Signaler aux autorités si nécessaire (arnaque financière)
