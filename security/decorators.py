from functools import wraps
from flask import jsonify, request, g
from flask_login import current_user

def require_vip(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentification requise'}), 401
        if not current_user.is_vip:
            return jsonify({'error': 'Abonnement VIP requis', 'upgrade_url': '/market'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_tokens(amount=1):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentification requise'}), 401
            if current_user.tokens < amount:
                return jsonify({
                    'error': 'Jetons insuffisants',
                    'tokens_required': amount,
                    'tokens_available': current_user.tokens,
                    'purchase_url': '/market'
                }), 402
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin(permission=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin = getattr(g, 'admin_user', None)
            if not admin:
                return jsonify({'error': 'Accès administrateur requis'}), 403
            if permission and not admin.has_permission(permission):
                return jsonify({'error': f'Permission requise: {permission}'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_active(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentification requise'}), 401
        if current_user.is_banned:
            return jsonify({
                'error': 'Compte suspendu',
                'reason': current_user.ban_reason or 'Violation des conditions d\'utilisation'
            }), 403
        if not current_user.is_active:
            return jsonify({'error': 'Compte désactivé'}), 403
        return f(*args, **kwargs)
    return decorated_function

def log_action(action_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            try:
                from models import db, AuditLog
                admin = getattr(g, 'admin_user', None)
                if admin:
                    log = AuditLog(
                        admin_id=admin.id,
                        action=action_type,
                        details=str(request.get_json() if request.is_json else request.form.to_dict()),
                        ip_address=request.remote_addr
                    )
                    db.session.add(log)
                    db.session.commit()
            except Exception as e:
                pass
            
            return result
        return decorated_function
    return decorator
