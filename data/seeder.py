import json
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def load_json_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def seed_database(db, models):
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
        print("Database already seeded, skipping...")
        return False
    
    print("Seeding database...")
    
    users_data = load_json_file('users.json')
    if users_data:
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
        print(f"Created {len(users_data)} users")
        
        demo_user = user_map.get('demo@shida.com')
        naomie = user_map.get('naomie@shida.com')
        sarah = user_map.get('sarah@shida.com')
        team = user_map.get('team@shida.com')
        
        if demo_user and naomie:
            match1 = Match(user1_id=demo_user.id, user2_id=naomie.id, compatibility_score=85.5)
            db.session.add(match1)
            db.session.flush()
            msg1 = Message(match_id=match1.id, sender_id=naomie.id, content="J'ai bien reçu votre offre...")
            db.session.add(msg1)
        
        if demo_user and sarah:
            match2 = Match(user1_id=demo_user.id, user2_id=sarah.id, compatibility_score=72.0)
            db.session.add(match2)
            db.session.flush()
            msg2 = Message(match_id=match2.id, sender_id=demo_user.id, content="Bonjour ! Ravi de faire votre connaissance")
            msg2_reply = Message(match_id=match2.id, sender_id=sarah.id, content="En attente de réponse", is_read=False)
            db.session.add(msg2)
            db.session.add(msg2_reply)
        
        if demo_user and team:
            match3 = Match(user1_id=demo_user.id, user2_id=team.id, compatibility_score=100.0)
            db.session.add(match3)
            db.session.flush()
            msg3 = Message(match_id=match3.id, sender_id=team.id, content="Bienvenue sur Shida ! Nous sommes ravis de vous accueillir. N'hésitez pas à nous contacter si vous avez des questions.")
            db.session.add(msg3)
            
            notif = Notification(
                user_id=demo_user.id,
                title="Bienvenue sur Shida !",
                message="Votre compte a été créé avec succès. Découvrez des profils compatibles.",
                notification_type="welcome"
            )
            db.session.add(notif)
        
        db.session.commit()
        print("Created demo matches and messages")
    
    pricing_data = load_json_file('pricing_plans.json')
    if pricing_data:
        for plan_data in pricing_data:
            plan = PricingPlan(
                name=plan_data['name'],
                plan_type=plan_data['plan_type'],
                price=plan_data['price'],
                currency=plan_data.get('currency', 'USD'),
                duration_days=plan_data.get('duration_days'),
                tokens_included=plan_data.get('tokens_included', 0),
                features=json.dumps(plan_data.get('features', [])),
                is_active=plan_data.get('is_active', True),
                is_featured=plan_data.get('is_featured', False)
            )
            db.session.add(plan)
        db.session.commit()
        print(f"Created {len(pricing_data)} pricing plans")
    
    promo_data = load_json_file('promo_codes.json')
    if promo_data:
        for code_data in promo_data:
            code = PromoCode(
                code=code_data['code'],
                discount_type=code_data['discount_type'],
                discount_value=code_data['discount_value'],
                max_uses=code_data.get('max_uses'),
                current_uses=code_data.get('current_uses', 0),
                valid_from=datetime.fromisoformat(code_data['valid_from']) if code_data.get('valid_from') else None,
                valid_until=datetime.fromisoformat(code_data['valid_until']) if code_data.get('valid_until') else None,
                is_active=code_data.get('is_active', True)
            )
            db.session.add(code)
        db.session.commit()
        print(f"Created {len(promo_data)} promo codes")
    
    content_data = load_json_file('content_pages.json')
    if content_data:
        for page_data in content_data:
            page = ContentPage(
                slug=page_data['slug'],
                title=page_data['title'],
                content=page_data['content'],
                is_published=page_data.get('is_published', True)
            )
            db.session.add(page)
        db.session.commit()
        print(f"Created {len(content_data)} content pages")
    
    config_data = load_json_file('matching_config.json')
    if config_data:
        for conf_data in config_data:
            config = MatchingConfig(
                name=conf_data['name'],
                religion_weight=conf_data.get('religion_weight', 0.2),
                location_weight=conf_data.get('location_weight', 0.15),
                objective_weight=conf_data.get('objective_weight', 0.35),
                profession_weight=conf_data.get('profession_weight', 0.1),
                age_weight=conf_data.get('age_weight', 0.15),
                interests_weight=conf_data.get('interests_weight', 0.05),
                is_active=conf_data.get('is_active', False)
            )
            db.session.add(config)
        db.session.commit()
        print(f"Created {len(config_data)} matching configs")
    
    print("Database seeding completed!")
    return True
