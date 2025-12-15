from datetime import datetime, timedelta
from models import db, User, Message, Like, Report
import re

class FraudDetector:
    SPAM_THRESHOLD = 5
    SUSPICIOUS_PATTERNS = [
        r'envoie[rz]?\s*(de l\')?argent',
        r'western\s*union',
        r'money\s*gram',
        r'carte\s*(de)?\s*cr[eé]dit',
        r'num[eé]ro\s*(de)?\s*compte',
        r'bitcoin|crypto',
        r'investis',
        r'h[eé]ritage',
        r'loterie',
        r'gagnant',
        r'\$\d+',
        r'€\d+',
        r'urgente?',
        r'secret',
        r'whatsapp|telegram|viber',
        r'\+\d{10,}',
    ]
    
    @staticmethod
    def check_message(content, sender_id):
        if not content:
            return {'safe': True, 'score': 0}
        
        content_lower = content.lower()
        score = 0
        flags = []
        
        for pattern in FraudDetector.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content_lower):
                score += 10
                flags.append(f"Pattern suspect: {pattern}")
        
        if len(content) > 2000:
            score += 5
            flags.append("Message très long")
        
        if content.isupper() and len(content) > 20:
            score += 5
            flags.append("Message en majuscules")
        
        exclamation_count = content.count('!')
        if exclamation_count > 5:
            score += 3
            flags.append("Trop de points d'exclamation")
        
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_messages = Message.query.filter(
            Message.sender_id == sender_id,
            Message.created_at > hour_ago
        ).count()
        
        if recent_messages > 20:
            score += 15
            flags.append("Activité de messagerie élevée")
        
        similar_messages = Message.query.filter(
            Message.sender_id == sender_id,
            Message.content == content
        ).count()
        
        if similar_messages > 2:
            score += 20
            flags.append("Messages répétitifs")
        
        is_safe = score < 30
        
        return {
            'safe': is_safe,
            'score': score,
            'flags': flags,
            'action': 'block' if score >= 50 else ('flag' if score >= 30 else 'allow')
        }
    
    @staticmethod
    def check_user_behavior(user):
        score = 0
        flags = []
        
        day_ago = datetime.utcnow() - timedelta(days=1)
        
        likes_sent = Like.query.filter(
            Like.sender_id == user.id,
            Like.created_at > day_ago
        ).count()
        
        if likes_sent > 200:
            score += 30
            flags.append(f"Trop de likes envoyés: {likes_sent}")
        elif likes_sent > 100:
            score += 15
            flags.append(f"Beaucoup de likes envoyés: {likes_sent}")
        
        messages_sent = Message.query.filter(
            Message.sender_id == user.id,
            Message.created_at > day_ago
        ).count()
        
        if messages_sent > 100:
            score += 25
            flags.append(f"Trop de messages envoyés: {messages_sent}")
        
        reports_received = Report.query.filter(
            Report.reported_user_id == user.id,
            Report.created_at > datetime.utcnow() - timedelta(days=7)
        ).count()
        
        if reports_received >= 3:
            score += 40
            flags.append(f"Plusieurs signalements reçus: {reports_received}")
        elif reports_received >= 1:
            score += 15
            flags.append(f"Signalement reçu: {reports_received}")
        
        if user.created_at and user.created_at > day_ago:
            if likes_sent > 50 or messages_sent > 20:
                score += 20
                flags.append("Nouveau compte avec activité suspecte")
        
        return {
            'suspicious': score >= 50,
            'score': score,
            'flags': flags,
            'recommended_action': 'ban' if score >= 80 else ('review' if score >= 50 else 'monitor' if score >= 30 else 'none')
        }
    
    @staticmethod
    def check_profile(profile):
        score = 0
        flags = []
        
        if not profile.photo_url:
            score += 10
            flags.append("Pas de photo")
        
        if not profile.bio:
            score += 5
            flags.append("Pas de bio")
        elif len(profile.bio) < 20:
            score += 3
            flags.append("Bio très courte")
        
        if profile.bio:
            bio_lower = profile.bio.lower()
            for pattern in FraudDetector.SUSPICIOUS_PATTERNS[:5]:
                if re.search(pattern, bio_lower):
                    score += 15
                    flags.append(f"Bio suspecte: {pattern}")
                    break
        
        if profile.age and (profile.age < 18 or profile.age > 100):
            score += 30
            flags.append(f"Âge suspect: {profile.age}")
        
        return {
            'suspicious': score >= 30,
            'score': score,
            'flags': flags
        }
    
    @staticmethod
    def auto_ban_check(user):
        behavior = FraudDetector.check_user_behavior(user)
        
        if behavior['score'] >= 80:
            from services.report_service import ReportService
            
            user.is_banned = True
            user.ban_reason = f"Détection automatique de fraude. Score: {behavior['score']}. Flags: {', '.join(behavior['flags'])}"
            user.banned_at = datetime.utcnow()
            db.session.commit()
            
            return True
        
        return False
