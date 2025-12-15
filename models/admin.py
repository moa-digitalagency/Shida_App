from datetime import datetime
from models.base import db


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
