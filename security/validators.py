import re
from html import escape

def validate_email(email):
    if not email:
        return False, "Email requis"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Format d'email invalide"
    
    if len(email) > 254:
        return False, "Email trop long"
    
    return True, None

def validate_password(password):
    if not password:
        return False, "Mot de passe requis"
    
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères"
    
    if len(password) > 128:
        return False, "Mot de passe trop long"
    
    return True, None

def sanitize_input(text, max_length=None):
    if not text:
        return ''
    
    text = str(text)
    
    text = escape(text)
    
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'data:text/html',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def validate_profile_data(data):
    errors = []
    
    if 'name' in data:
        name = data['name']
        if not name or len(name) < 2:
            errors.append("Le nom doit contenir au moins 2 caractères")
        elif len(name) > 100:
            errors.append("Le nom est trop long")
        elif not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', name):
            errors.append("Le nom contient des caractères invalides")
    
    if 'age' in data:
        try:
            age = int(data['age'])
            if age < 18:
                errors.append("Vous devez avoir au moins 18 ans")
            elif age > 120:
                errors.append("Âge invalide")
        except (ValueError, TypeError):
            errors.append("Âge invalide")
    
    if 'bio' in data and data['bio']:
        if len(data['bio']) > 1000:
            errors.append("La bio est trop longue (max 1000 caractères)")
    
    if 'photo_url' in data and data['photo_url']:
        url = data['photo_url']
        if not url.startswith(('http://', 'https://')):
            errors.append("URL de photo invalide")
        if len(url) > 500:
            errors.append("URL de photo trop longue")
    
    valid_objectives = ['Amitié', 'Construction', 'Mariage', 'Mariage & Sérieux']
    if 'objective' in data and data['objective']:
        if data['objective'] not in valid_objectives:
            errors.append("Objectif invalide")
    
    return len(errors) == 0, errors

def validate_message_content(content):
    if not content:
        return False, "Message vide"
    
    if len(content) > 5000:
        return False, "Message trop long"
    
    spam_patterns = [
        r'(.)\1{10,}',
        r'https?://[^\s]+\.[^\s]+',
    ]
    
    spam_score = 0
    for pattern in spam_patterns:
        if re.search(pattern, content):
            spam_score += 1
    
    if spam_score >= 2:
        return False, "Message potentiellement spam"
    
    return True, None

def validate_report_data(data):
    errors = []
    
    valid_types = [
        'inappropriate_content',
        'harassment',
        'fake_profile',
        'spam',
        'scam',
        'underage',
        'other'
    ]
    
    if 'report_type' in data:
        if data['report_type'] not in valid_types:
            errors.append("Type de signalement invalide")
    
    if 'reason' in data:
        if not data['reason'] or len(data['reason']) < 10:
            errors.append("Veuillez fournir une raison détaillée (min 10 caractères)")
        elif len(data['reason']) > 2000:
            errors.append("Raison trop longue")
    
    return len(errors) == 0, errors
