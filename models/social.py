from datetime import datetime
import json
from models.base import db


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
