from models import db, User, TokenTransaction, PricingPlan, PromoCode, Subscription
from datetime import datetime, timedelta
import json

class TokenService:
    BASE_TOKENS = 5
    VIP_BONUS = {
        'free': 0,
        'Gold': 30,
        'Platinum': 100
    }
    
    TOKEN_COSTS = {
        'greet_match': 1,
        'super_like': 3,
        'boost_profile': 5,
        'see_likes': 2,
        'undo_swipe': 1
    }
    
    @staticmethod
    def get_initial_tokens(vip_type='free'):
        return TokenService.BASE_TOKENS + TokenService.VIP_BONUS.get(vip_type, 0)
    
    @staticmethod
    def can_afford(user, action):
        cost = TokenService.TOKEN_COSTS.get(action, 1)
        return user.tokens >= cost
    
    @staticmethod
    def use_tokens(user, action, description=None):
        cost = TokenService.TOKEN_COSTS.get(action, 1)
        
        if user.tokens < cost:
            return {'success': False, 'error': 'Jetons insuffisants', 'tokens_needed': cost - user.tokens}
        
        user.tokens -= cost
        
        transaction = TokenTransaction(
            user_id=user.id,
            amount=-cost,
            transaction_type='use',
            description=description or f"Utilisation: {action}"
        )
        db.session.add(transaction)
        db.session.commit()
        
        from services.notification_service import NotificationService
        if user.tokens <= 3:
            NotificationService.send_low_tokens_warning(user)
        
        return {'success': True, 'tokens_remaining': user.tokens, 'tokens_used': cost}
    
    @staticmethod
    def add_tokens(user, amount, transaction_type='purchase', description=None, price=None, payment_method=None, payment_reference=None):
        user.tokens += amount
        
        transaction = TokenTransaction(
            user_id=user.id,
            amount=amount,
            transaction_type=transaction_type,
            description=description or f"Achat de {amount} jetons",
            price=price,
            payment_method=payment_method,
            payment_reference=payment_reference
        )
        db.session.add(transaction)
        db.session.commit()
        
        return {'success': True, 'tokens_total': user.tokens, 'tokens_added': amount}
    
    @staticmethod
    def purchase_token_pack(user, plan_id, payment_method=None, payment_reference=None):
        plan = PricingPlan.query.get(plan_id)
        if not plan or not plan.is_active:
            return {'success': False, 'error': 'Plan non disponible'}
        
        if plan.plan_type != 'tokens':
            return {'success': False, 'error': 'Ce plan n\'est pas un pack de jetons'}
        
        result = TokenService.add_tokens(
            user,
            plan.tokens_included,
            transaction_type='purchase',
            description=f"Achat pack: {plan.name}",
            price=plan.price,
            payment_method=payment_method,
            payment_reference=payment_reference
        )
        
        return result
    
    @staticmethod
    def apply_promo_code(user, code_str):
        code = PromoCode.query.filter_by(code=code_str.upper(), is_active=True).first()
        if not code:
            return {'success': False, 'error': 'Code promo invalide'}
        
        now = datetime.utcnow()
        if code.valid_from and now < code.valid_from:
            return {'success': False, 'error': 'Code promo pas encore valide'}
        if code.valid_until and now > code.valid_until:
            return {'success': False, 'error': 'Code promo expiré'}
        
        if code.max_uses and code.current_uses >= code.max_uses:
            return {'success': False, 'error': 'Code promo épuisé'}
        
        existing = TokenTransaction.query.filter_by(
            user_id=user.id,
            description=f"Code promo: {code.code}"
        ).first()
        if existing:
            return {'success': False, 'error': 'Vous avez déjà utilisé ce code'}
        
        if code.discount_type == 'tokens':
            TokenService.add_tokens(
                user,
                int(code.discount_value),
                transaction_type='promo',
                description=f"Code promo: {code.code}"
            )
            result = {'bonus_tokens': int(code.discount_value)}
        elif code.discount_type == 'trial':
            user.is_vip = True
            user.vip_type = 'Gold'
            user.vip_expires_at = datetime.utcnow() + timedelta(days=int(code.discount_value))
            db.session.commit()
            result = {'trial_days': int(code.discount_value)}
        else:
            result = {'discount_percent': code.discount_value}
        
        code.current_uses += 1
        db.session.commit()
        
        return {'success': True, **result}
    
    @staticmethod
    def get_transaction_history(user, limit=50):
        transactions = TokenTransaction.query.filter_by(user_id=user.id).order_by(
            TokenTransaction.created_at.desc()
        ).limit(limit).all()
        
        return [t.to_dict() for t in transactions]
    
    @staticmethod
    def get_available_plans():
        plans = PricingPlan.query.filter_by(is_active=True).order_by(PricingPlan.price).all()
        return [p.to_dict() for p in plans]
