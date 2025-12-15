OBJECTIVES = [
    'Amitié',
    'Construction',
    'Mariage',
    'Mariage & Sérieux'
]

RELIGIONS = [
    'Chrétienne',
    'Catholique',
    'Protestante',
    'Musulmane',
    'Autre',
    'Non spécifié'
]

TRIBES = [
    'Gombe',
    'Kinshasa',
    'Lubumbashi',
    'Bukavu',
    'Autre',
    'Non spécifié'
]

PROFESSIONS = [
    'Entrepreneur',
    'Médecin',
    'Ingénieur',
    'Enseignant',
    'Artiste',
    'Avocat',
    'Commerçant',
    'Étudiant',
    'Fonctionnaire',
    'Autre'
]

VIP_TYPES = {
    'free': {
        'name': 'Free',
        'tokens_per_month': 5,
        'can_see_likes': False,
        'ghost_mode': False,
        'unlimited_swipes': False
    },
    'Gold': {
        'name': 'VIP Gold',
        'tokens_per_month': 30,
        'can_see_likes': True,
        'ghost_mode': True,
        'unlimited_swipes': True
    },
    'Platinum': {
        'name': 'VIP Platinum',
        'tokens_per_month': 100,
        'can_see_likes': True,
        'ghost_mode': True,
        'unlimited_swipes': True,
        'priority_support': True
    }
}
