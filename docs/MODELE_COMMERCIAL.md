# Modèle Commercial - Shida

## Présentation

Shida est une application de rencontre orientée vers le marché africain francophone, principalement la République Démocratique du Congo. Le modèle commercial repose sur deux piliers: les abonnements VIP et les jetons à usage unique.

## Sources de Revenus

### 1. Abonnements VIP

#### VIP Gold
- **Mensuel**: 9.99 USD
- **Annuel**: 79.99 USD (économie de 40%)

**Avantages:**
- 30 jetons bonus à l'inscription
- Mode fantôme (navigation invisible)
- Voir qui vous a liké
- Badge VIP Gold visible sur le profil
- Accès aux filtres avancés

#### VIP Platinum
- **Mensuel**: 19.99 USD
- **Annuel**: 149.99 USD (économie de 37%)

**Avantages:**
- Tous les avantages Gold
- 100 jetons bonus à l'inscription
- Badge VIP Platinum
- Priorité dans les résultats de recherche
- Support prioritaire

### 2. Packs de Jetons

Les jetons sont une monnaie virtuelle utilisée pour certaines actions:

| Pack | Prix | Jetons | Coût/jeton |
|------|------|--------|------------|
| Découverte | 1.99 USD | 5 | 0.40 USD |
| Standard | 4.99 USD | 15 | 0.33 USD |
| Premium | 14.99 USD | 50 | 0.30 USD |
| Mega | 24.99 USD | 100 | 0.25 USD |

### 3. Utilisation des Jetons

| Action | Coût |
|--------|------|
| Saluer un nouveau match | 1 jeton |
| Super Like | 3 jetons |
| Boost de profil | 5 jetons |
| Voir qui m'a liké (non-VIP) | 2 jetons |
| Annuler un swipe | 1 jeton |

## Codes Promotionnels

Système de codes promo pour acquisition et rétention:

### Types de codes

1. **Réduction pourcentage**
   - Réduction sur le prix d'achat
   - Exemple: WELCOME10 (-10% sur premier achat)

2. **Jetons bonus**
   - Ajout de jetons gratuits
   - Exemple: BONUS5 (+5 jetons gratuits)

3. **Essai VIP**
   - Période d'essai VIP gratuite
   - Exemple: VIP50 (50% de réduction VIP)

### Codes pré-configurés

| Code | Type | Valeur | Max utilisations | Expiration |
|------|------|--------|------------------|------------|
| WELCOME10 | % | 10% | 1000 | 90 jours |
| VIP50 | % | 50% | 100 | 30 jours |
| BONUS5 | jetons | 5 | 500 | 60 jours |
| LAUNCH20 | % + jetons | 20% + 2 jetons | 200 | 45 jours |
| SPECIAL100 | % | 100% | 10 | 7 jours |

## Stratégie de Monétisation

### Modèle Freemium

**Utilisateur gratuit:**
- Création de compte
- Swipe limité à 100/heure
- Voir les matchs
- Envoyer des messages (coûte 1 jeton par nouveau match)
- 5 jetons offerts à l'inscription

**Conversion vers payant:**
- Notification quand jetons faibles
- Blocage "voir qui vous a liké" pour non-VIP
- Affichage du nombre de likes reçus (sans les profils)
- Mode fantôme réservé VIP

### Entonnoir de Conversion

1. **Inscription**: 10 jetons gratuits
2. **Premiers swipes**: Utilisation naturelle
3. **Premier match**: Besoin d'1 jeton pour saluer
4. **Likes reçus**: Notification "X personnes vous ont liké"
5. **Blocage**: "Passez VIP pour voir"
6. **Conversion**: Achat VIP ou jetons

## Gestion des Abonnements

### Cycle de vie

1. **Souscription**
   - Paiement immédiat
   - Activation VIP instantanée
   - Jetons bonus crédités

2. **Période active**
   - Accès aux fonctionnalités VIP
   - Renouvellement automatique activé par défaut

3. **Expiration proche** (J-3)
   - Notification de renouvellement
   - Possibilité de désactiver le renouvellement

4. **Expiration**
   - Retour au statut gratuit
   - Conservation des jetons non utilisés
   - Historique des matchs préservé

### Annulation

L'utilisateur peut annuler le renouvellement automatique à tout moment. L'abonnement reste actif jusqu'à la fin de la période payée.

## Indicateurs Clés (KPIs)

### Acquisition
- Nombre d'inscriptions par jour/semaine/mois
- Source des inscriptions
- Coût d'acquisition client (CAC)

### Engagement
- Utilisateurs actifs quotidiens (DAU)
- Utilisateurs actifs mensuels (MAU)
- Ratio DAU/MAU
- Nombre de swipes/matchs/messages

### Monétisation
- Revenu mensuel récurrent (MRR)
- Revenu moyen par utilisateur (ARPU)
- Taux de conversion gratuit vers payant
- Valeur vie client (LTV)
- Ratio LTV/CAC

### Rétention
- Taux de rétention J1, J7, J30
- Taux de désabonnement (churn)
- Durée moyenne d'abonnement

## Tableau de Bord Admin

L'interface admin fournit:

### Statistiques en temps réel
- Utilisateurs totaux et nouveaux
- Utilisateurs actifs (7 derniers jours)
- Nombre de matchs et messages
- Signalements en attente

### Revenus
- Chiffre d'affaires mensuel
- Abonnements actifs
- Jetons vendus
- Valeur moyenne des transactions

### Graphiques
- Courbe d'inscriptions (7 jours)
- Distribution par âge
- Distribution par objectif (Mariage, Amitié, etc.)

## Paiements

### Méthodes supportées (à implémenter)
- Mobile Money (Orange Money, M-Pesa, Airtel Money)
- Cartes bancaires
- PayPal

### Sécurité
- Références de paiement stockées
- Historique des transactions
- Pas de stockage de données de carte

## Projections

### Modèle de revenus (exemple)

Hypothèses:
- 10 000 utilisateurs actifs mensuels
- 5% conversion VIP
- 10% achat de jetons
- Prix moyen VIP: 12 USD/mois
- Prix moyen jetons: 5 USD

**Revenus mensuels estimés:**
- VIP: 500 users x 12 USD = 6 000 USD
- Jetons: 1 000 achats x 5 USD = 5 000 USD
- **Total: 11 000 USD/mois**

## Évolutions Futures

### Court terme
- Intégration paiement mobile money
- Pack "boost" pour visibilité 24h
- Jetons offerts pour invitation d'amis

### Moyen terme
- Abonnement entreprise (agences matrimoniales)
- Publicités ciblées pour utilisateurs gratuits
- Cadeaux virtuels entre utilisateurs

### Long terme
- Événements de rencontre organisés
- Services de coaching relationnel
- Expansion vers d'autres pays africains
