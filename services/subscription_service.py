from models import db, User, Subscription, PricingPlan, TokenTransaction
from datetime import datetime, timedelta

class SubscriptionService:
    @staticmethod
    def get_user_subscription(user):
        subscription = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).order_by(Subscription.expires_at.desc()).first()
        
        if subscription and subscription.expires_at:
            if subscription.expires_at < datetime.utcnow():
                subscription.status = 'expired'
                user.is_vip = False
                user.vip_type = 'free'
                db.session.commit()
                return None
        
        return subscription.to_dict() if subscription else None
    
    @staticmethod
    def subscribe(user, plan_id, payment_method=None, payment_reference=None):
        plan = PricingPlan.query.get(plan_id)
        if not plan or not plan.is_active:
            return {'success': False, 'error': 'Plan non disponible'}
        
        if plan.plan_type != 'subscription':
            return {'success': False, 'error': 'Ce plan n\'est pas un abonnement'}
        
        existing = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        if existing:
            existing.status = 'cancelled'
        
        expires_at = datetime.utcnow() + timedelta(days=plan.duration_days) if plan.duration_days else None
        
        subscription = Subscription(
            user_id=user.id,
            plan_type=plan.name,
            price=plan.price,
            currency=plan.currency,
            payment_method=payment_method,
            payment_reference=payment_reference,
            status='active',
            starts_at=datetime.utcnow(),
            expires_at=expires_at,
            auto_renew=True
        )
        db.session.add(subscription)
        
        vip_type = 'Gold'
        if 'Platinum' in plan.name:
            vip_type = 'Platinum'
        
        user.is_vip = True
        user.vip_type = vip_type
        user.vip_expires_at = expires_at
        
        if plan.tokens_included and plan.tokens_included > 0:
            user.tokens += plan.tokens_included
            
            transaction = TokenTransaction(
                user_id=user.id,
                amount=plan.tokens_included,
                transaction_type='subscription_bonus',
                description=f"Bonus abonnement: {plan.name}",
                price=0
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        return {
            'success': True,
            'subscription': subscription.to_dict(),
            'vip_type': vip_type,
            'tokens_added': plan.tokens_included or 0
        }
    
    @staticmethod
    def cancel_subscription(user, reason=None):
        subscription = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if not subscription:
            return {'success': False, 'error': 'Aucun abonnement actif'}
        
        subscription.auto_renew = False
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Renouvellement automatique désactivé',
            'expires_at': subscription.expires_at.isoformat() if subscription.expires_at else None
        }
    
    @staticmethod
    def check_expiring_subscriptions():
        threshold = datetime.utcnow() + timedelta(days=3)
        
        expiring = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.expires_at <= threshold,
            Subscription.expires_at > datetime.utcnow()
        ).all()
        
        from services.notification_service import NotificationService
        
        for sub in expiring:
            days_remaining = (sub.expires_at - datetime.utcnow()).days
            NotificationService.send_vip_expiring_notification(sub.user, days_remaining)
        
        return len(expiring)
    
    @staticmethod
    def process_expired_subscriptions():
        expired = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.expires_at < datetime.utcnow()
        ).all()
        
        for sub in expired:
            sub.status = 'expired'
            sub.user.is_vip = False
            sub.user.vip_type = 'free'
        
        db.session.commit()
        return len(expired)
    
    @staticmethod
    def get_subscription_history(user, limit=10):
        subscriptions = Subscription.query.filter_by(user_id=user.id).order_by(
            Subscription.created_at.desc()
        ).limit(limit).all()
        
        return [s.to_dict() for s in subscriptions]
    
    @staticmethod
    def get_available_plans(plan_type=None):
        query = PricingPlan.query.filter_by(is_active=True)
        if plan_type:
            query = query.filter_by(plan_type=plan_type)
        
        plans = query.order_by(PricingPlan.price).all()
        return [p.to_dict() for p in plans]
