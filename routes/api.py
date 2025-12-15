from flask import Blueprint, jsonify, request
from models import db, User, Profile, Like, Match, Message, Notification, Report, PricingPlan
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from security.validators import validate_email, validate_password, sanitize_input, validate_profile_data
from security.rate_limiter import rate_limiter

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/auth/register', methods=['POST'])
def register():
    ip = request.remote_addr
    allowed, error = rate_limiter.check_rate_limit(ip, 'register')
    if not allowed:
        return jsonify({'error': error}), 429
    
    data = request.get_json()
    
    email = sanitize_input(data.get('email', ''))
    valid, error = validate_email(email)
    if not valid:
        return jsonify({'error': error}), 400
    
    password = data.get('password', '')
    valid, error = validate_password(password)
    if not valid:
        return jsonify({'error': error}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400
    
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        tokens=10,
        ip_address=ip
    )
    db.session.add(user)
    db.session.commit()
    
    name = sanitize_input(data.get('name', 'Nouvel utilisateur'), max_length=100)
    age = data.get('age', 25)
    try:
        age = int(age)
        if age < 18:
            age = 18
        elif age > 120:
            age = 25
    except:
        age = 25
    
    profile = Profile(
        user_id=user.id,
        name=name,
        age=age,
        objective=data.get('objective', 'Amitié')
    )
    db.session.add(profile)
    db.session.commit()
    
    from services.notification_service import NotificationService
    NotificationService.send_welcome_notification(user)
    
    login_user(user)
    return jsonify({'success': True, 'user': user.to_dict()})

@api.route('/auth/login', methods=['POST'])
def login():
    ip = request.remote_addr
    allowed, error = rate_limiter.check_rate_limit(ip, 'login')
    if not allowed:
        return jsonify({'error': error}), 429
    
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        if user.is_banned:
            return jsonify({
                'error': 'Compte suspendu',
                'reason': user.ban_reason or 'Violation des conditions d\'utilisation'
            }), 403
        
        user.last_login = datetime.utcnow()
        user.ip_address = ip
        db.session.commit()
        
        login_user(user)
        rate_limiter.reset(ip, 'login')
        return jsonify({'success': True, 'user': user.to_dict()})
    
    return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

@api.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@api.route('/auth/me')
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())

@api.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'GET':
        return jsonify(current_user.profile.to_dict() if current_user.profile else {})
    
    data = request.get_json()
    
    valid, errors = validate_profile_data(data)
    if not valid:
        return jsonify({'error': errors[0], 'errors': errors}), 400
    
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id, name='', age=25)
        db.session.add(profile)
    
    allowed_fields = ['name', 'age', 'bio', 'photo_url', 'religion', 'tribe', 'profession', 'objective', 'interests', 'location']
    for field in allowed_fields:
        if field in data:
            value = data[field]
            if field in ['name', 'bio', 'profession', 'location']:
                value = sanitize_input(value)
            setattr(profile, field, value)
    
    db.session.commit()
    return jsonify(profile.to_dict())

@api.route('/profile/ghost-mode', methods=['POST'])
@login_required
def toggle_ghost_mode():
    if not current_user.is_vip:
        return jsonify({'error': 'Fonctionnalité VIP requise', 'upgrade_url': '/market'}), 403
    
    current_user.ghost_mode = not current_user.ghost_mode
    db.session.commit()
    return jsonify({'ghost_mode': current_user.ghost_mode})

@api.route('/profile/verification', methods=['POST'])
@login_required
def submit_verification():
    data = request.get_json()
    photo_url = data.get('photo_url')
    
    if not photo_url:
        return jsonify({'error': 'Photo de vérification requise'}), 400
    
    from services.verification_service import VerificationService
    result = VerificationService.submit_verification(current_user, photo_url)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400

@api.route('/discovery')
@login_required
def get_discovery_profiles():
    from services.match_service import MatchService
    profiles = MatchService.get_discovery_profiles(current_user, limit=20)
    return jsonify([p.to_dict() for p in profiles])

@api.route('/discovery/swipe', methods=['POST'])
@login_required
def swipe():
    ip = request.remote_addr
    allowed, error = rate_limiter.check_rate_limit(f"{current_user.id}", 'swipe')
    if not allowed:
        return jsonify({'error': error}), 429
    
    data = request.get_json()
    profile_id = data.get('profile_id')
    direction = data.get('direction')
    
    target_profile = Profile.query.get(profile_id)
    if not target_profile:
        return jsonify({'error': 'Profil non trouvé'}), 404
    
    if direction == 'right':
        from services.match_service import MatchService
        result = MatchService.process_like(current_user, target_profile.user_id)
        
        if result.get('match'):
            return jsonify({
                'match': True,
                'match_data': result.get('match_data'),
                'compatibility_score': result.get('compatibility_score')
            })
    else:
        target_profile.views_count = (target_profile.views_count or 0) + 1
        db.session.commit()
    
    return jsonify({'match': False})

@api.route('/matches')
@login_required
def get_matches():
    from services.match_service import MatchService
    matches = MatchService.get_user_matches(current_user)
    return jsonify(matches)

@api.route('/matches/<int:match_id>/messages')
@login_required
def get_messages(match_id):
    match = Match.query.get_or_404(match_id)
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    messages = Message.query.filter_by(match_id=match_id).order_by(Message.created_at).all()
    
    Message.query.filter_by(match_id=match_id).filter(
        Message.sender_id != current_user.id
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify([m.to_dict() for m in messages])

@api.route('/matches/<int:match_id>/messages', methods=['POST'])
@login_required
def send_message(match_id):
    allowed, error = rate_limiter.check_rate_limit(f"{current_user.id}", 'message')
    if not allowed:
        return jsonify({'error': error}), 429
    
    match = Match.query.get_or_404(match_id)
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    data = request.get_json()
    content = sanitize_input(data.get('content', ''), max_length=5000)
    
    if not content:
        return jsonify({'error': 'Message vide'}), 400
    
    from security.fraud_detection import FraudDetector
    fraud_check = FraudDetector.check_message(content, current_user.id)
    if fraud_check['action'] == 'block':
        return jsonify({'error': 'Message non autorisé'}), 400
    
    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content=content,
        is_flagged=fraud_check['action'] == 'flag'
    )
    db.session.add(message)
    db.session.commit()
    
    other_user = match.user2 if match.user1_id == current_user.id else match.user1
    from services.notification_service import NotificationService
    NotificationService.send_message_notification(other_user, current_user, match_id)
    
    return jsonify(message.to_dict())

@api.route('/matches/<int:match_id>/greet', methods=['POST'])
@login_required
def greet_match(match_id):
    if current_user.tokens < 1:
        return jsonify({
            'error': 'Jetons insuffisants',
            'tokens_required': 1,
            'tokens_available': current_user.tokens,
            'purchase_url': '/market'
        }), 402
    
    match = Match.query.get_or_404(match_id)
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    existing_message = Message.query.filter_by(match_id=match_id, sender_id=current_user.id).first()
    if existing_message:
        return jsonify({'error': 'Vous avez déjà salué ce match'}), 400
    
    from services.token_service import TokenService
    result = TokenService.use_tokens(current_user, 'greet_match', f"Salutation match #{match_id}")
    
    if not result['success']:
        return jsonify(result), 400
    
    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content="Bonjour ! Ravi de faire votre connaissance 👋"
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'tokens_remaining': result['tokens_remaining'],
        'message': message.to_dict()
    })

@api.route('/likes/received')
@login_required
def get_likes_received():
    from services.match_service import MatchService
    result = MatchService.get_likes_received(current_user)
    return jsonify(result)

@api.route('/tokens/use', methods=['POST'])
@login_required
def use_token():
    data = request.get_json()
    action = data.get('action', 'greet_match')
    
    from services.token_service import TokenService
    result = TokenService.use_tokens(current_user, action)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400

@api.route('/tokens/history')
@login_required
def get_token_history():
    from services.token_service import TokenService
    history = TokenService.get_transaction_history(current_user)
    return jsonify(history)

@api.route('/market/plans')
@login_required
def get_market_plans():
    from services.subscription_service import SubscriptionService
    plans = SubscriptionService.get_available_plans()
    return jsonify(plans)

@api.route('/market/purchase', methods=['POST'])
@login_required
def purchase_plan():
    data = request.get_json()
    plan_id = data.get('plan_id')
    
    plan = PricingPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan non trouvé'}), 404
    
    if plan.plan_type == 'tokens':
        from services.token_service import TokenService
        result = TokenService.purchase_token_pack(current_user, plan_id)
    else:
        from services.subscription_service import SubscriptionService
        result = SubscriptionService.subscribe(current_user, plan_id)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400

@api.route('/market/promo', methods=['POST'])
@login_required
def apply_promo():
    data = request.get_json()
    code = data.get('code', '')
    
    from services.token_service import TokenService
    result = TokenService.apply_promo_code(current_user, code)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400

@api.route('/subscription')
@login_required
def get_subscription():
    from services.subscription_service import SubscriptionService
    subscription = SubscriptionService.get_user_subscription(current_user)
    return jsonify(subscription or {'active': False})

@api.route('/subscription/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    from services.subscription_service import SubscriptionService
    result = SubscriptionService.cancel_subscription(current_user)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400

@api.route('/notifications')
@login_required
def get_notifications():
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    from services.notification_service import NotificationService
    notifications = NotificationService.get_user_notifications(current_user, unread_only=unread_only)
    unread_count = NotificationService.get_unread_count(current_user)
    return jsonify({'notifications': notifications, 'unread_count': unread_count})

@api.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    from services.notification_service import NotificationService
    NotificationService.mark_as_read(notification_id, current_user.id)
    return jsonify({'success': True})

@api.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    from services.notification_service import NotificationService
    NotificationService.mark_all_as_read(current_user.id)
    return jsonify({'success': True})

@api.route('/report', methods=['POST'])
@login_required
def create_report():
    allowed, error = rate_limiter.check_rate_limit(f"{current_user.id}", 'report')
    if not allowed:
        return jsonify({'error': error}), 429
    
    data = request.get_json()
    
    from services.report_service import ReportService
    result = ReportService.create_report(
        reporter=current_user,
        reported_user_id=data.get('user_id'),
        reported_message_id=data.get('message_id'),
        report_type=data.get('report_type', 'other'),
        reason=sanitize_input(data.get('reason', ''), max_length=2000)
    )
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400

@api.route('/dashboard/stats')
@login_required
def get_dashboard_stats():
    from services.gamification_service import GamificationService
    stats = GamificationService.get_dashboard_data(current_user)
    return jsonify(stats)

@api.route('/gamification/badges')
@login_required
def get_badges():
    from services.gamification_service import GamificationService
    badges = GamificationService.get_user_badges(current_user)
    return jsonify(badges)

@api.route('/gamification/achievements')
@login_required
def get_achievements():
    from services.gamification_service import GamificationService
    achievements = GamificationService.get_user_achievements(current_user)
    return jsonify(achievements)

@api.route('/gamification/level')
@login_required
def get_level():
    from services.gamification_service import GamificationService
    level = GamificationService.get_user_level(current_user)
    return jsonify(level)
