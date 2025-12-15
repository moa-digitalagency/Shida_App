import os
import logging
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, 
    static_folder='statics',
    template_folder='templates'
)

app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable is required")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

from models import db
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'views.index'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

from routes.api import api
from routes.views import views
from routes.admin import admin

app.register_blueprint(api)
app.register_blueprint(views)
app.register_blueprint(admin)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

with app.app_context():
    from models import User, Profile, Like, Match, Message, AdminUser, Report, Subscription, TokenTransaction, Notification, AuditLog, SupportTicket, TicketResponse, ContentPage, MatchingConfig, PricingPlan, PromoCode
    db.create_all()
    
    from werkzeug.security import generate_password_hash
    import json
    
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@shida.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_password and not AdminUser.query.filter_by(email=admin_email).first():
        admin_user = AdminUser(
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            name='Super Admin',
            role='super_admin'
        )
        db.session.add(admin_user)
        db.session.commit()
    
    if not User.query.filter_by(email='demo@shida.com').first():
        demo_user = User(
            email='demo@shida.com',
            password_hash=generate_password_hash('demo123'),
            is_vip=True,
            vip_type='Gold',
            tokens=12
        )
        db.session.add(demo_user)
        db.session.commit()
        
        demo_profile = Profile(
            user_id=demo_user.id,
            name='Demo User',
            age=28,
            bio='Looking for meaningful connections',
            religion='Chrétienne',
            tribe='Gombe',
            profession='Entrepreneur',
            objective='Mariage',
            views_count=34,
            weekly_views=json.dumps([8, 5, 6, 7, 10, 12, 8]),
            is_verified=True
        )
        db.session.add(demo_profile)
        
        sample_users = [
            {'name': 'Nadia', 'age': 27, 'photo': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400', 'objective': 'Mariage & Sérieux'},
            {'name': 'Naomie', 'age': 25, 'photo': 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400', 'objective': 'Mariage & Sérieux'},
            {'name': 'Sarah', 'age': 28, 'photo': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400', 'objective': 'Construction'},
            {'name': 'Grace', 'age': 24, 'photo': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400', 'objective': 'Amitié'},
            {'name': 'Michelle', 'age': 26, 'photo': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400', 'objective': 'Mariage'},
        ]
        
        for data in sample_users:
            user = User(
                email=f'{data["name"].lower()}@shida.com',
                password_hash=generate_password_hash('password123'),
                tokens=10
            )
            db.session.add(user)
            db.session.commit()
            
            profile = Profile(
                user_id=user.id,
                name=data['name'],
                age=data['age'],
                photo_url=data['photo'],
                objective=data['objective'],
                religion='Chrétienne',
                profession='Professionnelle'
            )
            db.session.add(profile)
        
        db.session.commit()
        
        naomie_user = User.query.join(Profile).filter(Profile.name == 'Naomie').first()
        sarah_user = User.query.join(Profile).filter(Profile.name == 'Sarah').first()
        
        if naomie_user:
            match1 = Match(user1_id=demo_user.id, user2_id=naomie_user.id)
            db.session.add(match1)
            db.session.commit()
            msg1 = Message(match_id=match1.id, sender_id=naomie_user.id, content="J'ai bien reçu votre offre...")
            db.session.add(msg1)
        
        if sarah_user:
            match2 = Match(user1_id=demo_user.id, user2_id=sarah_user.id)
            db.session.add(match2)
            db.session.commit()
            msg2 = Message(match_id=match2.id, sender_id=sarah_user.id, content="En attente de réponse")
            db.session.add(msg2)
        
        shida_team = User(
            email='team@shida.com',
            password_hash=generate_password_hash('shidateam'),
            is_vip=True
        )
        db.session.add(shida_team)
        db.session.commit()
        
        team_profile = Profile(
            user_id=shida_team.id,
            name='Équipe Shida',
            age=0,
            photo_url='https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400'
        )
        db.session.add(team_profile)
        
        match3 = Match(user1_id=demo_user.id, user2_id=shida_team.id)
        db.session.add(match3)
        db.session.commit()
        msg3 = Message(match_id=match3.id, sender_id=shida_team.id, content="Bienvenue sur Shida !")
        db.session.add(msg3)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
