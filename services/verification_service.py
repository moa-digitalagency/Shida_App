from models import db, User, Profile, AuditLog
from datetime import datetime

class VerificationService:
    VERIFICATION_STATUSES = ['pending', 'approved', 'rejected']
    
    @staticmethod
    def submit_verification(user, photo_url):
        if not user.profile:
            return {'success': False, 'error': 'Profil non trouvé'}
        
        if user.profile.is_verified:
            return {'success': False, 'error': 'Profil déjà vérifié'}
        
        user.profile.verification_photo = photo_url
        user.profile.verification_status = 'pending'
        db.session.commit()
        
        return {'success': True, 'status': 'pending', 'message': 'Demande de vérification soumise'}
    
    @staticmethod
    def get_pending_verifications(limit=50):
        profiles = Profile.query.filter_by(
            verification_status='pending'
        ).order_by(Profile.id.desc()).limit(limit).all()
        
        result = []
        for profile in profiles:
            result.append({
                'user_id': profile.user_id,
                'profile': profile.to_dict(),
                'verification_photo': profile.verification_photo,
                'submitted_at': profile.user.created_at.isoformat() if profile.user else None
            })
        
        return result
    
    @staticmethod
    def approve_verification(user_id, admin_id=None):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {'success': False, 'error': 'Profil non trouvé'}
        
        profile.is_verified = True
        profile.verification_status = 'approved'
        
        if admin_id:
            log = AuditLog(
                admin_id=admin_id,
                action='verification_approved',
                target_type='user',
                target_id=user_id,
                details=f"Vérification approuvée pour {profile.name}"
            )
            db.session.add(log)
        
        db.session.commit()
        
        from services.notification_service import NotificationService
        user = User.query.get(user_id)
        if user:
            NotificationService.send_verification_notification(user, approved=True)
        
        return {'success': True, 'message': 'Vérification approuvée'}
    
    @staticmethod
    def reject_verification(user_id, reason=None, admin_id=None):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {'success': False, 'error': 'Profil non trouvé'}
        
        profile.verification_status = 'rejected'
        profile.verification_photo = None
        
        if admin_id:
            log = AuditLog(
                admin_id=admin_id,
                action='verification_rejected',
                target_type='user',
                target_id=user_id,
                details=f"Vérification refusée pour {profile.name}. Raison: {reason or 'Non spécifiée'}"
            )
            db.session.add(log)
        
        db.session.commit()
        
        from services.notification_service import NotificationService
        user = User.query.get(user_id)
        if user:
            NotificationService.send_verification_notification(user, approved=False)
        
        return {'success': True, 'message': 'Vérification refusée'}
    
    @staticmethod
    def get_verification_status(user):
        if not user.profile:
            return {'status': 'no_profile', 'is_verified': False}
        
        return {
            'status': user.profile.verification_status,
            'is_verified': user.profile.is_verified,
            'has_pending': user.profile.verification_status == 'pending'
        }
