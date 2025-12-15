from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_vip = db.Column(db.Boolean, default=False)
    vip_type = db.Column(db.String(20), default='free')
    vip_expires_at = db.Column(db.DateTime)
    tokens = db.Column(db.Integer, default=5)
    ghost_mode = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text)
    banned_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String(50))
    device_info = db.Column(db.Text)
    
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    sent_likes = db.relationship('Like', foreign_keys='Like.sender_id', backref='sender', lazy='dynamic')
    received_likes = db.relationship('Like', foreign_keys='Like.receiver_id', backref='receiver', lazy='dynamic')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic')
    token_transactions = db.relationship('TokenTransaction', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_vip': self.is_vip,
            'vip_type': self.vip_type,
            'tokens': self.tokens,
            'ghost_mode': self.ghost_mode,
            'is_active': self.is_active,
            'is_banned': self.is_banned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile': self.profile.to_dict() if self.profile else None
        }

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    photos = db.Column(db.Text)
    religion = db.Column(db.String(50))
    tribe = db.Column(db.String(50))
    profession = db.Column(db.String(100))
    objective = db.Column(db.String(50))
    interests = db.Column(db.Text)
    location = db.Column(db.String(100))
    views_count = db.Column(db.Integer, default=0)
    weekly_views = db.Column(db.Text, default='[0,0,0,0,0,0,0]')
    is_verified = db.Column(db.Boolean, default=False)
    verification_photo = db.Column(db.String(500))
    verification_status = db.Column(db.String(20), default='pending')
    is_approved = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'bio': self.bio,
            'photo_url': self.photo_url,
            'photos': json.loads(self.photos) if self.photos else [],
            'religion': self.religion,
            'tribe': self.tribe,
            'profession': self.profession,
            'objective': self.objective,
            'interests': self.interests,
            'location': self.location,
            'views_count': self.views_count,
            'weekly_views': json.loads(self.weekly_views) if self.weekly_views else [0]*7,
            'is_verified': self.is_verified
        }

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_match = db.Column(db.Boolean, default=False)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    compatibility_score = db.Column(db.Float, default=0.0)
    
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    messages = db.relationship('Message', backref='match', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user1': self.user1.profile.to_dict() if self.user1.profile else None,
            'user2': self.user2.profile.to_dict() if self.user2.profile else None,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'compatibility_score': self.compatibility_score
        }

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(100))
    
    sender = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.profile.name if self.sender.profile else 'Unknown',
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read
        }

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='moderator')
    permissions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def get_permissions(self):
        if self.role == 'super_admin':
            return ['all']
        return json.loads(self.permissions) if self.permissions else []
    
    def has_permission(self, permission):
        if self.role == 'super_admin':
            return True
        perms = self.get_permissions()
        return permission in perms or 'all' in perms
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reported_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    report_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    resolution_notes = db.Column(db.Text)
    action_taken = db.Column(db.String(50))
    
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    reported_message = db.relationship('Message')
    resolver = db.relationship('AdminUser')
    
    def to_dict(self):
        return {
            'id': self.id,
            'reporter': self.reporter.profile.name if self.reporter.profile else self.reporter.email,
            'reported_user': self.reported_user.profile.name if self.reported_user and self.reported_user.profile else None,
            'report_type': self.report_type,
            'reason': self.reason,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'action_taken': self.action_taken
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')
    starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'price': self.price,
            'currency': self.currency,
            'status': self.status,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class TokenTransaction(db.Model):
    __tablename__ = 'token_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='general')
    is_read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('AdminUser')
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_name': self.admin.name if self.admin else 'Unknown',
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='other')
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='medium')
    assigned_to = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    user = db.relationship('User')
    assignee = db.relationship('AdminUser')
    responses = db.relationship('TicketResponse', backref='ticket', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.profile.name if self.user.profile else self.user.email,
            'subject': self.subject,
            'category': self.category,
            'message': self.message,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }

class TicketResponse(db.Model):
    __tablename__ = 'ticket_responses'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('AdminUser')
    user = db.relationship('User')

class ContentPage(db.Model):
    __tablename__ = 'content_pages'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'content': self.content,
            'is_published': self.is_published,
            'updated_at': self.updated_at.isoformat()
        }

class MatchingConfig(db.Model):
    __tablename__ = 'matching_config'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    religion_weight = db.Column(db.Float, default=0.2)
    location_weight = db.Column(db.Float, default=0.15)
    objective_weight = db.Column(db.Float, default=0.3)
    profession_weight = db.Column(db.Float, default=0.1)
    age_weight = db.Column(db.Float, default=0.15)
    interests_weight = db.Column(db.Float, default=0.1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'religion_weight': self.religion_weight,
            'location_weight': self.location_weight,
            'objective_weight': self.objective_weight,
            'profession_weight': self.profession_weight,
            'age_weight': self.age_weight,
            'interests_weight': self.interests_weight,
            'is_active': self.is_active
        }

class PricingPlan(db.Model):
    __tablename__ = 'pricing_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    duration_days = db.Column(db.Integer)
    tokens_included = db.Column(db.Integer, default=0)
    features = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'plan_type': self.plan_type,
            'price': self.price,
            'currency': self.currency,
            'duration_days': self.duration_days,
            'tokens_included': self.tokens_included,
            'features': json.loads(self.features) if self.features else [],
            'is_active': self.is_active,
            'is_featured': self.is_featured
        }

class PromoCode(db.Model):
    __tablename__ = 'promo_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    max_uses = db.Column(db.Integer)
    current_uses = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'is_active': self.is_active
        }
