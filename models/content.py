from datetime import datetime
from models.base import db


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
