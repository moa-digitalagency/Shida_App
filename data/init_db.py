"""
Init DB Script - Creates initial database data directly without JSON files.
This script is designed to work in production deployments.
"""
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


def init_database(db, models):
    """Initialize database with hardcoded seed data for production deployment."""
    User = models.User
    Profile = models.Profile
    Match = models.Match
    Message = models.Message
    PricingPlan = models.PricingPlan
    PromoCode = models.PromoCode
    ContentPage = models.ContentPage
    MatchingConfig = models.MatchingConfig
    AdminUser = models.AdminUser
    Notification = models.Notification
    
    if User.query.count() > 0:
        print("Database already initialized, skipping...")
        return False
    
    print("Initializing database with seed data...")
    
    users_data = [
        {
            "email": "demo@shida.com",
            "password": "demo123",
            "is_vip": True,
            "vip_type": "Gold",
            "tokens": 12,
            "profile": {
                "name": "Demo User",
                "age": 28,
                "bio": "Looking for meaningful connections",
                "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
                "religion": "Chrétienne",
                "tribe": "Gombe",
                "profession": "Entrepreneur",
                "objective": "Mariage",
                "location": "Kinshasa",
                "views_count": 34,
                "weekly_views": [8, 5, 6, 7, 10, 12, 8],
                "is_verified": True
            }
        },
        {
            "email": "nadia@shida.com",
            "password": "password123",
            "is_vip": False,
            "vip_type": "free",
            "tokens": 10,
            "profile": {
                "name": "Nadia",
                "age": 27,
                "bio": "Femme ambitieuse cherchant une relation sérieuse",
                "photo_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400",
                "religion": "Chrétienne",
                "tribe": "Kinshasa",
                "profession": "Médecin",
                "objective": "Mariage & Sérieux",
                "location": "Kinshasa",
                "views_count": 56,
                "weekly_views": [12, 8, 9, 11, 7, 5, 4],
                "is_verified": True
            }
        },
        {
            "email": "naomie@shida.com",
            "password": "password123",
            "is_vip": True,
            "vip_type": "Gold",
            "tokens": 25,
            "profile": {
                "name": "Naomie",
                "age": 25,
                "bio": "Passionnée de musique et de voyages",
                "photo_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400",
                "religion": "Catholique",
                "tribe": "Lubumbashi",
                "profession": "Artiste",
                "objective": "Mariage & Sérieux",
                "location": "Lubumbashi",
                "views_count": 89,
                "weekly_views": [15, 12, 18, 14, 10, 12, 8],
                "is_verified": True
            }
        },
        {
            "email": "sarah@shida.com",
            "password": "password123",
            "is_vip": False,
            "vip_type": "free",
            "tokens": 8,
            "profile": {
                "name": "Sarah",
                "age": 28,
                "bio": "Ingénieure en informatique, amoureuse des défis",
                "photo_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
                "religion": "Protestante",
                "tribe": "Gombe",
                "profession": "Ingénieur",
                "objective": "Construction",
                "location": "Kinshasa",
                "views_count": 45,
                "weekly_views": [6, 8, 7, 5, 9, 6, 4],
                "is_verified": False
            }
        },
        {
            "email": "grace@shida.com",
            "password": "password123",
            "is_vip": False,
            "vip_type": "free",
            "tokens": 5,
            "profile": {
                "name": "Grace",
                "age": 24,
                "bio": "Étudiante en droit, passionnée de lecture",
                "photo_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400",
                "religion": "Chrétienne",
                "tribe": "Bukavu",
                "profession": "Étudiant",
                "objective": "Amitié",
                "location": "Bukavu",
                "views_count": 32,
                "weekly_views": [4, 5, 6, 4, 5, 4, 4],
                "is_verified": True
            }
        },
        {
            "email": "michelle@shida.com",
            "password": "password123",
            "is_vip": True,
            "vip_type": "Platinum",
            "tokens": 50,
            "profile": {
                "name": "Michelle",
                "age": 26,
                "bio": "Avocate spécialisée en droit des affaires",
                "photo_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400",
                "religion": "Catholique",
                "tribe": "Kinshasa",
                "profession": "Avocat",
                "objective": "Mariage",
                "location": "Kinshasa",
                "views_count": 78,
                "weekly_views": [10, 12, 14, 11, 13, 10, 8],
                "is_verified": True
            }
        },
        {
            "email": "jessica@shida.com",
            "password": "password123",
            "is_vip": False,
            "vip_type": "free",
            "tokens": 15,
            "profile": {
                "name": "Jessica",
                "age": 29,
                "bio": "Entrepreneure dans le secteur de la mode",
                "photo_url": "https://images.unsplash.com/photo-1488716820095-cbe80883c496?w=400",
                "religion": "Chrétienne",
                "tribe": "Gombe",
                "profession": "Entrepreneur",
                "objective": "Mariage & Sérieux",
                "location": "Kinshasa",
                "views_count": 67,
                "weekly_views": [9, 11, 10, 8, 12, 9, 8],
                "is_verified": True
            }
        },
        {
            "email": "claudine@shida.com",
            "password": "password123",
            "is_vip": False,
            "vip_type": "free",
            "tokens": 7,
            "profile": {
                "name": "Claudine",
                "age": 23,
                "bio": "Étudiante en médecine, rêveuse et optimiste",
                "photo_url": "https://images.unsplash.com/photo-1502323777036-f29e3972f2e0?w=400",
                "religion": "Protestante",
                "tribe": "Lubumbashi",
                "profession": "Étudiant",
                "objective": "Amitié",
                "location": "Lubumbashi",
                "views_count": 28,
                "weekly_views": [3, 4, 5, 4, 5, 4, 3],
                "is_verified": False
            }
        },
        {
            "email": "team@shida.com",
            "password": "shidateam2024",
            "is_vip": True,
            "vip_type": "Platinum",
            "tokens": 999,
            "is_system": True,
            "profile": {
                "name": "Équipe Shida",
                "age": 0,
                "bio": "Bienvenue sur Shida ! Nous sommes là pour vous aider.",
                "photo_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400",
                "religion": "",
                "tribe": "",
                "profession": "Support",
                "objective": "",
                "location": "Kinshasa",
                "views_count": 0,
                "weekly_views": [0, 0, 0, 0, 0, 0, 0],
                "is_verified": True
            }
        }
    ]
    
    user_map = {}
    for user_data in users_data:
        user = User(
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            is_vip=user_data.get('is_vip', False),
            vip_type=user_data.get('vip_type', 'free'),
            tokens=user_data.get('tokens', 5),
            created_at=datetime.utcnow()
        )
        if user_data.get('is_vip'):
            user.vip_expires_at = datetime.utcnow() + timedelta(days=30)
        
        db.session.add(user)
        db.session.flush()
        
        profile_data = user_data.get('profile', {})
        profile = Profile(
            user_id=user.id,
            name=profile_data.get('name', 'Utilisateur'),
            age=profile_data.get('age', 25),
            bio=profile_data.get('bio', ''),
            photo_url=profile_data.get('photo_url', ''),
            religion=profile_data.get('religion', ''),
            tribe=profile_data.get('tribe', ''),
            profession=profile_data.get('profession', ''),
            objective=profile_data.get('objective', 'Amitié'),
            location=profile_data.get('location', ''),
            views_count=profile_data.get('views_count', 0),
            weekly_views=json.dumps(profile_data.get('weekly_views', [0]*7)),
            is_verified=profile_data.get('is_verified', False)
        )
        db.session.add(profile)
        user_map[user_data['email']] = user
    
    db.session.commit()
    print(f"Created {len(users_data)} users with profiles")
    
    demo_user = user_map.get('demo@shida.com')
    naomie = user_map.get('naomie@shida.com')
    sarah = user_map.get('sarah@shida.com')
    team = user_map.get('team@shida.com')
    
    if demo_user and naomie:
        match1 = Match(user1_id=demo_user.id, user2_id=naomie.id, compatibility_score=85)
        db.session.add(match1)
        db.session.flush()
        
        msg1 = Message(match_id=match1.id, sender_id=naomie.id, content="Bonjour ! Ravie de faire ta connaissance 😊")
        msg2 = Message(match_id=match1.id, sender_id=demo_user.id, content="Salut ! Le plaisir est partagé. Ton profil est très intéressant !")
        db.session.add_all([msg1, msg2])
    
    if demo_user and sarah:
        match2 = Match(user1_id=demo_user.id, user2_id=sarah.id, compatibility_score=72)
        db.session.add(match2)
    
    if demo_user and team:
        match3 = Match(user1_id=team.id, user2_id=demo_user.id, compatibility_score=100)
        db.session.add(match3)
        db.session.flush()
        
        welcome_msg = Message(
            match_id=match3.id,
            sender_id=team.id,
            content="Bienvenue sur Shida ! 🎉 Nous sommes ravis de vous accueillir. N'hésitez pas à nous contacter si vous avez des questions."
        )
        db.session.add(welcome_msg)
        
        notif = Notification(
            user_id=demo_user.id,
            type='welcome',
            title='Bienvenue sur Shida !',
            message='Découvrez comment trouver votre partenaire idéal.',
            data=json.dumps({'action': 'start_discovery'})
        )
        db.session.add(notif)
    
    db.session.commit()
    print("Created demo matches and messages")
    
    pricing_plans = [
        {"name": "5 Jetons", "description": "Pack découverte", "price": 1.99, "tokens": 5, "plan_type": "tokens", "is_popular": False},
        {"name": "15 Jetons", "description": "Pack standard", "price": 4.99, "tokens": 15, "plan_type": "tokens", "is_popular": True},
        {"name": "50 Jetons", "description": "Pack premium", "price": 14.99, "tokens": 50, "plan_type": "tokens", "is_popular": False},
        {"name": "VIP Gold", "description": "Accès VIP Gold pendant 30 jours", "price": 9.99, "duration_days": 30, "plan_type": "subscription", "is_popular": True, "vip_type": "Gold"},
        {"name": "VIP Platinum", "description": "Accès VIP Platinum pendant 30 jours", "price": 19.99, "duration_days": 30, "plan_type": "subscription", "is_popular": False, "vip_type": "Platinum"},
        {"name": "VIP Gold Annuel", "description": "Accès VIP Gold pendant 1 an", "price": 79.99, "duration_days": 365, "plan_type": "subscription", "is_popular": False, "vip_type": "Gold"},
        {"name": "VIP Platinum Annuel", "description": "Accès VIP Platinum pendant 1 an", "price": 149.99, "duration_days": 365, "plan_type": "subscription", "is_popular": False, "vip_type": "Platinum"},
        {"name": "100 Jetons", "description": "Mega pack", "price": 24.99, "tokens": 100, "plan_type": "tokens", "is_popular": False}
    ]
    
    for plan_data in pricing_plans:
        plan = PricingPlan(
            name=plan_data['name'],
            description=plan_data.get('description', ''),
            price=plan_data['price'],
            tokens=plan_data.get('tokens', 0),
            duration_days=plan_data.get('duration_days', 0),
            plan_type=plan_data['plan_type'],
            is_popular=plan_data.get('is_popular', False),
            vip_type=plan_data.get('vip_type', '')
        )
        db.session.add(plan)
    db.session.commit()
    print(f"Created {len(pricing_plans)} pricing plans")
    
    promo_codes = [
        {"code": "WELCOME10", "discount_percent": 10, "bonus_tokens": 0, "max_uses": 1000, "expires_at": datetime.utcnow() + timedelta(days=90)},
        {"code": "VIP50", "discount_percent": 50, "bonus_tokens": 0, "max_uses": 100, "expires_at": datetime.utcnow() + timedelta(days=30)},
        {"code": "BONUS5", "discount_percent": 0, "bonus_tokens": 5, "max_uses": 500, "expires_at": datetime.utcnow() + timedelta(days=60)},
        {"code": "LAUNCH20", "discount_percent": 20, "bonus_tokens": 2, "max_uses": 200, "expires_at": datetime.utcnow() + timedelta(days=45)},
        {"code": "SPECIAL100", "discount_percent": 100, "bonus_tokens": 10, "max_uses": 10, "expires_at": datetime.utcnow() + timedelta(days=7)}
    ]
    
    for promo_data in promo_codes:
        promo = PromoCode(
            code=promo_data['code'],
            discount_percent=promo_data['discount_percent'],
            bonus_tokens=promo_data['bonus_tokens'],
            max_uses=promo_data['max_uses'],
            expires_at=promo_data['expires_at']
        )
        db.session.add(promo)
    db.session.commit()
    print(f"Created {len(promo_codes)} promo codes")
    
    content_pages = [
        {"title": "Conditions d'utilisation", "slug": "terms", "content": "<h1>Conditions d'utilisation</h1><p>Bienvenue sur Shida...</p>", "is_published": True},
        {"title": "Politique de confidentialité", "slug": "privacy", "content": "<h1>Politique de confidentialité</h1><p>Votre vie privée est importante...</p>", "is_published": True},
        {"title": "FAQ", "slug": "faq", "content": "<h1>Questions fréquentes</h1><p>Retrouvez ici les réponses...</p>", "is_published": True},
        {"title": "Contact", "slug": "contact", "content": "<h1>Nous contacter</h1><p>Pour toute question...</p>", "is_published": True},
        {"title": "À propos", "slug": "about", "content": "<h1>À propos de Shida</h1><p>Shida est une application de rencontre...</p>", "is_published": True}
    ]
    
    for page_data in content_pages:
        page = ContentPage(
            title=page_data['title'],
            slug=page_data['slug'],
            content=page_data['content'],
            is_published=page_data['is_published']
        )
        db.session.add(page)
    db.session.commit()
    print(f"Created {len(content_pages)} content pages")
    
    matching_configs = [
        {"name": "Standard", "age_weight": 0.2, "religion_weight": 0.3, "tribe_weight": 0.15, "location_weight": 0.25, "profession_weight": 0.05, "interests_weight": 0.05, "is_active": True},
        {"name": "Religion Focus", "age_weight": 0.1, "religion_weight": 0.5, "tribe_weight": 0.1, "location_weight": 0.2, "profession_weight": 0.05, "interests_weight": 0.05, "is_active": False},
        {"name": "Location Focus", "age_weight": 0.15, "religion_weight": 0.15, "tribe_weight": 0.1, "location_weight": 0.5, "profession_weight": 0.05, "interests_weight": 0.05, "is_active": False}
    ]
    
    for conf_data in matching_configs:
        config = MatchingConfig(
            name=conf_data['name'],
            age_weight=conf_data['age_weight'],
            religion_weight=conf_data['religion_weight'],
            tribe_weight=conf_data['tribe_weight'],
            location_weight=conf_data['location_weight'],
            profession_weight=conf_data['profession_weight'],
            interests_weight=conf_data['interests_weight'],
            is_active=conf_data['is_active']
        )
        db.session.add(config)
    db.session.commit()
    print(f"Created {len(matching_configs)} matching configs")
    
    print("Database initialization completed!")
    return True
