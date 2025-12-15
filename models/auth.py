from flask_login import UserMixin
from datetime import datetime
import json
from models.base import db


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
