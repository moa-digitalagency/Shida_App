from functools import wraps
from flask import jsonify
from flask_login import current_user

def require_vip(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_vip:
            return jsonify({'error': 'VIP subscription required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_tokens(amount=1):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            if current_user.tokens < amount:
                return jsonify({'error': 'Insufficient tokens'}), 402
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(text):
    if not text:
        return ''
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None
