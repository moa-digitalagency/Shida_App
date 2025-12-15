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
    is_vip = db.Column(db.Boolean, default=False)
    vip_type = db.Column(db.String(20), default='free')
    tokens = db.Column(db.Integer, default=5)
    ghost_mode = db.Column(db.Boolean, default=False)
    
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    sent_likes = db.relationship('Like', foreign_keys='Like.sender_id', backref='sender', lazy='dynamic')
    received_likes = db.relationship('Like', foreign_keys='Like.receiver_id', backref='receiver', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_vip': self.is_vip,
            'vip_type': self.vip_type,
            'tokens': self.tokens,
            'ghost_mode': self.ghost_mode,
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
    religion = db.Column(db.String(50))
    tribe = db.Column(db.String(50))
    profession = db.Column(db.String(100))
    objective = db.Column(db.String(50))
    interests = db.Column(db.Text)
    views_count = db.Column(db.Integer, default=0)
    weekly_views = db.Column(db.Text, default='[0,0,0,0,0,0,0]')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'bio': self.bio,
            'photo_url': self.photo_url,
            'religion': self.religion,
            'tribe': self.tribe,
            'profession': self.profession,
            'objective': self.objective,
            'interests': self.interests,
            'views_count': self.views_count,
            'weekly_views': json.loads(self.weekly_views) if self.weekly_views else [0]*7
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
    
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    messages = db.relationship('Message', backref='match', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user1': self.user1.profile.to_dict() if self.user1.profile else None,
            'user2': self.user2.profile.to_dict() if self.user2.profile else None,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
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
