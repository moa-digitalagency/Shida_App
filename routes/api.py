from flask import Blueprint, jsonify, request, session
from models import db, User, Profile, Like, Match, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import json
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        email=data.get('email'),
        password_hash=generate_password_hash(data.get('password')),
        tokens=10
    )
    db.session.add(user)
    db.session.commit()
    
    profile = Profile(
        user_id=user.id,
        name=data.get('name', 'New User'),
        age=data.get('age', 25),
        objective=data.get('objective', 'Amitié')
    )
    db.session.add(profile)
    db.session.commit()
    
    login_user(user)
    return jsonify({'success': True, 'user': user.to_dict()})

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        login_user(user)
        return jsonify({'success': True, 'user': user.to_dict()})
    return jsonify({'error': 'Invalid credentials'}), 401

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
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
    
    for field in ['name', 'age', 'bio', 'photo_url', 'religion', 'tribe', 'profession', 'objective', 'interests']:
        if field in data:
            setattr(profile, field, data[field])
    
    db.session.commit()
    return jsonify(profile.to_dict())

@api.route('/profile/ghost-mode', methods=['POST'])
@login_required
def toggle_ghost_mode():
    current_user.ghost_mode = not current_user.ghost_mode
    db.session.commit()
    return jsonify({'ghost_mode': current_user.ghost_mode})

@api.route('/discovery')
@login_required
def get_discovery_profiles():
    liked_ids = [l.receiver_id for l in current_user.sent_likes]
    liked_ids.append(current_user.id)
    
    profiles = Profile.query.filter(
        ~Profile.user_id.in_(liked_ids),
        Profile.user_id != current_user.id
    ).limit(20).all()
    
    return jsonify([p.to_dict() for p in profiles])

@api.route('/discovery/swipe', methods=['POST'])
@login_required
def swipe():
    data = request.get_json()
    profile_id = data.get('profile_id')
    direction = data.get('direction')
    
    target_profile = Profile.query.get(profile_id)
    if not target_profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    target_profile.views_count += 1
    weekly_views = json.loads(target_profile.weekly_views or '[0,0,0,0,0,0,0]')
    day_index = datetime.now().weekday()
    weekly_views[day_index] += 1
    target_profile.weekly_views = json.dumps(weekly_views)
    
    if direction == 'right':
        like = Like(sender_id=current_user.id, receiver_id=target_profile.user_id)
        db.session.add(like)
        
        mutual_like = Like.query.filter_by(
            sender_id=target_profile.user_id,
            receiver_id=current_user.id
        ).first()
        
        if mutual_like:
            like.is_match = True
            mutual_like.is_match = True
            match = Match(user1_id=current_user.id, user2_id=target_profile.user_id)
            db.session.add(match)
            
            welcome_msg = Message(
                match_id=match.id,
                sender_id=target_profile.user_id,
                content="Bienvenue sur Shida !"
            )
            db.session.add(welcome_msg)
            db.session.commit()
            
            return jsonify({
                'match': True,
                'match_data': match.to_dict()
            })
    
    db.session.commit()
    return jsonify({'match': False})

@api.route('/matches')
@login_required
def get_matches():
    matches = Match.query.filter(
        db.or_(Match.user1_id == current_user.id, Match.user2_id == current_user.id),
        Match.is_active == True
    ).all()
    
    result = []
    for match in matches:
        other_user = match.user2 if match.user1_id == current_user.id else match.user1
        last_message = Message.query.filter_by(match_id=match.id).order_by(Message.created_at.desc()).first()
        unread_count = Message.query.filter_by(
            match_id=match.id,
            is_read=False
        ).filter(Message.sender_id != current_user.id).count()
        
        result.append({
            'id': match.id,
            'other_user': other_user.profile.to_dict() if other_user.profile else None,
            'last_message': last_message.to_dict() if last_message else None,
            'unread_count': unread_count
        })
    
    return jsonify(result)

@api.route('/matches/<int:match_id>/messages')
@login_required
def get_messages(match_id):
    match = Match.query.get_or_404(match_id)
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = Message.query.filter_by(match_id=match_id).order_by(Message.created_at).all()
    
    Message.query.filter_by(match_id=match_id).filter(
        Message.sender_id != current_user.id
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify([m.to_dict() for m in messages])

@api.route('/matches/<int:match_id>/messages', methods=['POST'])
@login_required
def send_message(match_id):
    match = Match.query.get_or_404(match_id)
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content=data.get('content')
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict())

@api.route('/tokens/use', methods=['POST'])
@login_required
def use_token():
    if current_user.tokens <= 0:
        return jsonify({'error': 'No tokens remaining'}), 400
    
    current_user.tokens -= 1
    db.session.commit()
    return jsonify({'tokens': current_user.tokens})

@api.route('/dashboard/stats')
@login_required
def get_dashboard_stats():
    profile = current_user.profile
    matches_count = Match.query.filter(
        db.or_(Match.user1_id == current_user.id, Match.user2_id == current_user.id)
    ).count()
    
    weekly_views = json.loads(profile.weekly_views) if profile and profile.weekly_views else [0]*7
    total_views = sum(weekly_views)
    last_week_views = sum(weekly_views[:len(weekly_views)//2]) if len(weekly_views) > 1 else 0
    change_percent = ((total_views - last_week_views) / max(last_week_views, 1)) * 100 if last_week_views > 0 else 12
    
    return jsonify({
        'views_total': profile.views_count if profile else 0,
        'views_weekly': weekly_views,
        'views_change_percent': round(change_percent),
        'tokens': current_user.tokens,
        'negotiations_count': matches_count,
        'is_vip': current_user.is_vip,
        'vip_type': current_user.vip_type
    })
