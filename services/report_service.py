from models import db, User, Report, Message, AuditLog
from datetime import datetime

class ReportService:
    REPORT_TYPES = [
        'inappropriate_content',
        'harassment',
        'fake_profile',
        'spam',
        'scam',
        'underage',
        'other'
    ]
    
    REPORT_PRIORITIES = ['low', 'medium', 'high', 'critical']
    
    ACTIONS = [
        'warning_sent',
        'content_removed',
        'temporary_ban',
        'permanent_ban',
        'dismissed'
    ]
    
    @staticmethod
    def create_report(reporter, reported_user_id=None, reported_message_id=None, report_type='other', reason=''):
        if not reported_user_id and not reported_message_id:
            return {'success': False, 'error': 'Cible du signalement requise'}
        
        if report_type not in ReportService.REPORT_TYPES:
            report_type = 'other'
        
        priority = 'medium'
        if report_type in ['harassment', 'scam', 'underage']:
            priority = 'high'
        if report_type == 'underage':
            priority = 'critical'
        
        report = Report(
            reporter_id=reporter.id,
            reported_user_id=reported_user_id,
            reported_message_id=reported_message_id,
            report_type=report_type,
            reason=reason,
            priority=priority,
            status='pending'
        )
        db.session.add(report)
        db.session.commit()
        
        return {'success': True, 'report_id': report.id}
    
    @staticmethod
    def get_pending_reports(priority=None, limit=50):
        query = Report.query.filter_by(status='pending')
        
        if priority:
            query = query.filter_by(priority=priority)
        
        reports = query.order_by(
            db.case(
                (Report.priority == 'critical', 1),
                (Report.priority == 'high', 2),
                (Report.priority == 'medium', 3),
                (Report.priority == 'low', 4)
            ),
            Report.created_at.asc()
        ).limit(limit).all()
        
        return [r.to_dict() for r in reports]
    
    @staticmethod
    def resolve_report(report_id, admin_id, action, notes=None):
        report = Report.query.get(report_id)
        if not report:
            return {'success': False, 'error': 'Signalement non trouvé'}
        
        if action not in ReportService.ACTIONS:
            return {'success': False, 'error': 'Action invalide'}
        
        report.status = 'resolved'
        report.resolved_at = datetime.utcnow()
        report.resolved_by = admin_id
        report.resolution_notes = notes
        report.action_taken = action
        
        if action == 'temporary_ban' and report.reported_user:
            report.reported_user.is_banned = True
            report.reported_user.ban_reason = f"Signalement #{report.id}: {report.report_type}"
            report.reported_user.banned_at = datetime.utcnow()
        
        elif action == 'permanent_ban' and report.reported_user:
            report.reported_user.is_banned = True
            report.reported_user.is_active = False
            report.reported_user.ban_reason = f"Ban permanent - Signalement #{report.id}: {report.report_type}"
            report.reported_user.banned_at = datetime.utcnow()
        
        elif action == 'content_removed' and report.reported_message:
            report.reported_message.content = "[Message supprimé par modération]"
            report.reported_message.is_flagged = True
            report.reported_message.flag_reason = f"Signalement #{report.id}"
        
        log = AuditLog(
            admin_id=admin_id,
            action=f'report_resolved_{action}',
            target_type='report',
            target_id=report_id,
            details=f"Signalement résolu. Action: {action}. Notes: {notes or 'Aucune'}"
        )
        db.session.add(log)
        db.session.commit()
        
        return {'success': True, 'action_taken': action}
    
    @staticmethod
    def get_report_stats():
        total = Report.query.count()
        pending = Report.query.filter_by(status='pending').count()
        resolved = Report.query.filter_by(status='resolved').count()
        
        by_type = db.session.query(
            Report.report_type,
            db.func.count(Report.id)
        ).group_by(Report.report_type).all()
        
        by_priority = db.session.query(
            Report.priority,
            db.func.count(Report.id)
        ).filter_by(status='pending').group_by(Report.priority).all()
        
        return {
            'total': total,
            'pending': pending,
            'resolved': resolved,
            'by_type': {t: c for t, c in by_type},
            'by_priority': {p: c for p, c in by_priority}
        }
    
    @staticmethod
    def unban_user(user_id, admin_id, reason=None):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'Utilisateur non trouvé'}
        
        if not user.is_banned:
            return {'success': False, 'error': 'Utilisateur non banni'}
        
        user.is_banned = False
        user.is_active = True
        user.ban_reason = None
        user.banned_at = None
        
        log = AuditLog(
            admin_id=admin_id,
            action='user_unbanned',
            target_type='user',
            target_id=user_id,
            details=f"Utilisateur débanni. Raison: {reason or 'Non spécifiée'}"
        )
        db.session.add(log)
        db.session.commit()
        
        return {'success': True, 'message': 'Utilisateur débanni'}
