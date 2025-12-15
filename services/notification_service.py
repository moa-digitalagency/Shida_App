from models import db, Notification, User
from datetime import datetime
import json

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, notification_type='general', action_url=None):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def send_welcome_notification(user):
        return NotificationService.create_notification(
            user.id,
            "Bienvenue sur Shida !",
            "Votre compte a été créé avec succès. Commencez à découvrir des profils compatibles.",
            notification_type='welcome',
            action_url='/discovery'
        )
    
    @staticmethod
    def send_match_notification(user, matched_user):
        matched_name = matched_user.profile.name if matched_user.profile else "Quelqu'un"
        return NotificationService.create_notification(
            user.id,
            "Affaire Conclue !",
            f"Vous avez un nouveau match avec {matched_name} ! Vous avez les mêmes objectifs.",
            notification_type='match',
            action_url='/negotiations'
        )
    
    @staticmethod
    def send_message_notification(user, sender, match_id):
        sender_name = sender.profile.name if sender.profile else "Quelqu'un"
        return NotificationService.create_notification(
            user.id,
            "Nouveau Message",
            f"{sender_name} vous a envoyé un message.",
            notification_type='message',
            action_url=f'/chat/{match_id}'
        )
    
    @staticmethod
    def send_like_notification(user):
        return NotificationService.create_notification(
            user.id,
            "Quelqu'un vous a liké !",
            "Vous avez reçu un nouveau like. Passez en VIP pour le découvrir.",
            notification_type='like',
            action_url='/market'
        )
    
    @staticmethod
    def send_profile_view_notification(user):
        return NotificationService.create_notification(
            user.id,
            "Quelqu'un a vu votre profil",
            "Votre profil a été consulté. Passez en VIP pour voir qui.",
            notification_type='view',
            action_url='/market'
        )
    
    @staticmethod
    def send_low_tokens_warning(user):
        return NotificationService.create_notification(
            user.id,
            "Jetons faibles",
            f"Il ne vous reste que {user.tokens} jeton(s). Rechargez pour continuer à faire des rencontres.",
            notification_type='tokens',
            action_url='/market'
        )
    
    @staticmethod
    def send_vip_expiring_notification(user, days_remaining):
        return NotificationService.create_notification(
            user.id,
            "Abonnement VIP",
            f"Votre abonnement VIP expire dans {days_remaining} jours. Renouvelez pour garder vos avantages.",
            notification_type='vip',
            action_url='/market'
        )
    
    @staticmethod
    def send_verification_notification(user, approved):
        if approved:
            return NotificationService.create_notification(
                user.id,
                "Profil Vérifié !",
                "Félicitations ! Votre profil a été vérifié. Vous avez maintenant le badge de vérification.",
                notification_type='verification',
                action_url='/profile'
            )
        else:
            return NotificationService.create_notification(
                user.id,
                "Vérification Refusée",
                "Votre demande de vérification a été refusée. Veuillez soumettre une nouvelle photo.",
                notification_type='verification',
                action_url='/profile'
            )
    
    @staticmethod
    def get_user_notifications(user, limit=50, unread_only=False):
        query = Notification.query.filter_by(user_id=user.id)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        return [n.to_dict() for n in notifications]
    
    @staticmethod
    def get_unread_count(user):
        return Notification.query.filter_by(user_id=user.id, is_read=False).count()
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True
