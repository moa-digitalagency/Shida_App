from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from functools import wraps
from models import db, User, Profile, AdminUser, Report, Subscription, TokenTransaction, Match, Message, Notification, AuditLog, SupportTicket, TicketResponse, ContentPage, MatchingConfig, PricingPlan, PromoCode, Like
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import json

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id:
            return redirect(url_for('admin.login'))
        admin_user = AdminUser.query.get(admin_id)
        if not admin_user or not admin_user.is_active:
            session.pop('admin_id', None)
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin_id = session.get('admin_id')
            if not admin_id:
                return redirect(url_for('admin.login'))
            admin_user = AdminUser.query.get(admin_id)
            if not admin_user or not admin_user.is_active:
                session.pop('admin_id', None)
                return redirect(url_for('admin.login'))
            if not admin_user.has_permission(permission):
                return render_template('admin/unauthorized.html', admin_user=admin_user), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_action(admin_id, action, target_type=None, target_id=None, details=None):
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin_user = AdminUser.query.filter_by(email=email).first()
        
        if admin_user and check_password_hash(admin_user.password_hash, password):
            if not admin_user.is_active:
                return render_template('admin/login.html', error='Compte désactivé')
            session['admin_id'] = admin_user.id
            admin_user.last_login = datetime.utcnow()
            db.session.commit()
            log_action(admin_user.id, 'login')
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/login.html', error='Identifiants invalides')
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    admin_id = session.get('admin_id')
    if admin_id:
        log_action(admin_id, 'logout')
    session.pop('admin_id', None)
    return redirect(url_for('admin.login'))

@admin.route('/')
@admin.route('/dashboard')
@admin_required
def dashboard():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_users': User.query.count(),
        'new_users_today': User.query.filter(func.date(User.created_at) == today).count(),
        'new_users_week': User.query.filter(User.created_at >= week_ago).count(),
        'active_users': User.query.filter(User.last_login >= week_ago).count(),
        'vip_users': User.query.filter(User.is_vip == True).count(),
        'total_matches': Match.query.count(),
        'matches_today': Match.query.filter(func.date(Match.created_at) == today).count(),
        'total_messages': Message.query.count(),
        'pending_reports': Report.query.filter(Report.status == 'pending').count(),
        'open_tickets': SupportTicket.query.filter(SupportTicket.status == 'open').count(),
        'revenue_month': db.session.query(func.sum(Subscription.price)).filter(Subscription.created_at >= month_ago).scalar() or 0,
        'tokens_sold': db.session.query(func.sum(TokenTransaction.amount)).filter(TokenTransaction.transaction_type == 'purchase', TokenTransaction.created_at >= month_ago).scalar() or 0
    }
    
    daily_signups = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = User.query.filter(func.date(User.created_at) == date).count()
        daily_signups.append({'date': date.strftime('%a'), 'count': count})
    
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_reports = Report.query.filter(Report.status == 'pending').order_by(desc(Report.created_at)).limit(5).all()
    
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/dashboard.html', 
                          stats=stats, 
                          daily_signups=daily_signups,
                          recent_users=recent_users,
                          recent_reports=recent_reports,
                          admin_user=admin_user)

@admin.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    vip = request.args.get('vip', 'all')
    search = request.args.get('search', '')
    
    query = User.query
    
    if status == 'active':
        query = query.filter(User.is_active == True, User.is_banned == False)
    elif status == 'banned':
        query = query.filter(User.is_banned == True)
    elif status == 'inactive':
        query = query.filter(User.is_active == False)
    
    if vip == 'yes':
        query = query.filter(User.is_vip == True)
    elif vip == 'no':
        query = query.filter(User.is_vip == False)
    
    if search:
        query = query.join(Profile, isouter=True).filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                Profile.name.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(desc(User.created_at)).paginate(page=page, per_page=20)
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/users.html', users=users, admin_user=admin_user)

@admin.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    matches = Match.query.filter(db.or_(Match.user1_id == user_id, Match.user2_id == user_id)).all()
    reports_received = Report.query.filter(Report.reported_user_id == user_id).all()
    reports_made = Report.query.filter(Report.reporter_id == user_id).all()
    transactions = TokenTransaction.query.filter(TokenTransaction.user_id == user_id).order_by(desc(TokenTransaction.created_at)).limit(20).all()
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/user_detail.html', 
                          user=user, 
                          matches=matches,
                          reports_received=reports_received,
                          reports_made=reports_made,
                          transactions=transactions,
                          admin_user=admin_user)

@admin.route('/users/<int:user_id>/action', methods=['POST'])
@admin_required
def user_action(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    admin_id = session['admin_id']
    
    if action == 'ban':
        user.is_banned = True
        user.ban_reason = request.form.get('reason', 'Violation des conditions')
        user.banned_at = datetime.utcnow()
        log_action(admin_id, 'ban_user', 'user', user_id, f'Reason: {user.ban_reason}')
    elif action == 'unban':
        user.is_banned = False
        user.ban_reason = None
        log_action(admin_id, 'unban_user', 'user', user_id)
    elif action == 'verify':
        if user.profile:
            user.profile.is_verified = True
            user.profile.verification_status = 'approved'
        log_action(admin_id, 'verify_user', 'user', user_id)
    elif action == 'add_tokens':
        amount = int(request.form.get('amount', 0))
        user.tokens += amount
        transaction = TokenTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type='admin_grant',
            description=f'Tokens ajoutés par admin'
        )
        db.session.add(transaction)
        log_action(admin_id, 'add_tokens', 'user', user_id, f'Amount: {amount}')
    elif action == 'set_vip':
        user.is_vip = True
        user.vip_type = request.form.get('vip_type', 'Gold')
        days = int(request.form.get('days', 30))
        user.vip_expires_at = datetime.utcnow() + timedelta(days=days)
        log_action(admin_id, 'set_vip', 'user', user_id, f'Type: {user.vip_type}, Days: {days}')
    elif action == 'remove_vip':
        user.is_vip = False
        user.vip_type = 'free'
        user.vip_expires_at = None
        log_action(admin_id, 'remove_vip', 'user', user_id)
    
    db.session.commit()
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin.route('/moderation')
@admin_required
def moderation():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    priority = request.args.get('priority', 'all')
    
    query = Report.query
    
    if status != 'all':
        query = query.filter(Report.status == status)
    if priority != 'all':
        query = query.filter(Report.priority == priority)
    
    reports = query.order_by(desc(Report.created_at)).paginate(page=page, per_page=20)
    
    stats = {
        'pending': Report.query.filter(Report.status == 'pending').count(),
        'in_progress': Report.query.filter(Report.status == 'in_progress').count(),
        'resolved': Report.query.filter(Report.status == 'resolved').count(),
        'high_priority': Report.query.filter(Report.priority == 'high', Report.status == 'pending').count()
    }
    
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/moderation.html', reports=reports, stats=stats, admin_user=admin_user)

@admin.route('/moderation/<int:report_id>', methods=['GET', 'POST'])
@admin_required
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    admin_id = session['admin_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'resolve':
            report.status = 'resolved'
            report.resolved_at = datetime.utcnow()
            report.resolved_by = admin_id
            report.resolution_notes = request.form.get('notes')
            report.action_taken = request.form.get('action_taken')
            
            if report.action_taken == 'ban_user' and report.reported_user:
                report.reported_user.is_banned = True
                report.reported_user.ban_reason = 'Signalement confirmé'
                report.reported_user.banned_at = datetime.utcnow()
            elif report.action_taken == 'warning' and report.reported_user:
                notification = Notification(
                    user_id=report.reported_user_id,
                    title='Avertissement',
                    message='Votre comportement a été signalé. Veuillez respecter nos règles.',
                    notification_type='warning'
                )
                db.session.add(notification)
            
            log_action(admin_id, 'resolve_report', 'report', report_id, f'Action: {report.action_taken}')
        elif action == 'escalate':
            report.priority = 'high'
            log_action(admin_id, 'escalate_report', 'report', report_id)
        elif action == 'in_progress':
            report.status = 'in_progress'
            log_action(admin_id, 'start_review_report', 'report', report_id)
        
        db.session.commit()
        return redirect(url_for('admin.moderation'))
    
    admin_user = AdminUser.query.get(session['admin_id'])
    return render_template('admin/report_detail.html', report=report, admin_user=admin_user)

@admin.route('/matching')
@admin_required
def matching():
    config = MatchingConfig.query.filter(MatchingConfig.is_active == True).first()
    if not config:
        config = MatchingConfig(
            name='Default',
            religion_weight=0.2,
            location_weight=0.15,
            objective_weight=0.3,
            profession_weight=0.1,
            age_weight=0.15,
            interests_weight=0.1,
            is_active=True
        )
        db.session.add(config)
        db.session.commit()
    
    stats = {
        'total_matches': Match.query.count(),
        'matches_today': Match.query.filter(func.date(Match.created_at) == datetime.utcnow().date()).count(),
        'avg_compatibility': db.session.query(func.avg(Match.compatibility_score)).scalar() or 0,
        'match_to_message_rate': 0
    }
    
    total_matches = Match.query.count()
    matches_with_messages = db.session.query(Match.id).join(Message).distinct().count()
    if total_matches > 0:
        stats['match_to_message_rate'] = round((matches_with_messages / total_matches) * 100, 1)
    
    admin_user = AdminUser.query.get(session['admin_id'])
    return render_template('admin/matching.html', config=config, stats=stats, admin_user=admin_user)

@admin.route('/matching/update', methods=['POST'])
@admin_required
def update_matching():
    config = MatchingConfig.query.filter(MatchingConfig.is_active == True).first()
    
    config.religion_weight = float(request.form.get('religion_weight', 0.2))
    config.location_weight = float(request.form.get('location_weight', 0.15))
    config.objective_weight = float(request.form.get('objective_weight', 0.3))
    config.profession_weight = float(request.form.get('profession_weight', 0.1))
    config.age_weight = float(request.form.get('age_weight', 0.15))
    config.interests_weight = float(request.form.get('interests_weight', 0.1))
    config.updated_at = datetime.utcnow()
    
    db.session.commit()
    log_action(session['admin_id'], 'update_matching_config', 'matching_config', config.id)
    
    return redirect(url_for('admin.matching'))

@admin.route('/analytics')
@admin_required
def analytics():
    today = datetime.utcnow().date()
    month_ago = today - timedelta(days=30)
    
    daily_users = []
    daily_matches = []
    daily_messages = []
    
    for i in range(30):
        date = today - timedelta(days=29-i)
        users_count = User.query.filter(func.date(User.created_at) == date).count()
        matches_count = Match.query.filter(func.date(Match.created_at) == date).count()
        messages_count = Message.query.filter(func.date(Message.created_at) == date).count()
        
        daily_users.append({'date': date.strftime('%d/%m'), 'count': users_count})
        daily_matches.append({'date': date.strftime('%d/%m'), 'count': matches_count})
        daily_messages.append({'date': date.strftime('%d/%m'), 'count': messages_count})
    
    age_distribution = db.session.query(
        func.floor(Profile.age / 10) * 10,
        func.count(Profile.id)
    ).group_by(func.floor(Profile.age / 10) * 10).all()
    
    objective_distribution = db.session.query(
        Profile.objective,
        func.count(Profile.id)
    ).group_by(Profile.objective).all()
    
    funnel = {
        'signups': User.query.filter(User.created_at >= month_ago).count(),
        'profiles_complete': Profile.query.join(User).filter(User.created_at >= month_ago, Profile.bio.isnot(None)).count(),
        'first_swipe': db.session.query(Like.sender_id).distinct().filter(Like.created_at >= month_ago).count(),
        'first_match': db.session.query(Match.user1_id).distinct().filter(Match.created_at >= month_ago).count(),
        'first_message': db.session.query(Message.sender_id).distinct().filter(Message.created_at >= month_ago).count(),
        'vip_conversion': User.query.filter(User.created_at >= month_ago, User.is_vip == True).count()
    }
    
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/analytics.html',
                          daily_users=daily_users,
                          daily_matches=daily_matches,
                          daily_messages=daily_messages,
                          age_distribution=age_distribution,
                          objective_distribution=objective_distribution,
                          funnel=funnel,
                          admin_user=admin_user)

@admin.route('/monetization')
@admin_required
def monetization():
    plans = PricingPlan.query.order_by(PricingPlan.plan_type, PricingPlan.price).all()
    promos = PromoCode.query.order_by(desc(PromoCode.created_at)).all()
    
    today = datetime.utcnow().date()
    month_ago = today - timedelta(days=30)
    
    stats = {
        'revenue_month': db.session.query(func.sum(Subscription.price)).filter(Subscription.created_at >= month_ago).scalar() or 0,
        'subscriptions_active': Subscription.query.filter(Subscription.status == 'active').count(),
        'tokens_sold_month': db.session.query(func.sum(TokenTransaction.amount)).filter(
            TokenTransaction.transaction_type == 'purchase',
            TokenTransaction.created_at >= month_ago
        ).scalar() or 0,
        'avg_transaction': db.session.query(func.avg(Subscription.price)).filter(Subscription.created_at >= month_ago).scalar() or 0
    }
    
    recent_transactions = Subscription.query.order_by(desc(Subscription.created_at)).limit(10).all()
    
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/monetization.html',
                          plans=plans,
                          promos=promos,
                          stats=stats,
                          recent_transactions=recent_transactions,
                          admin_user=admin_user)

@admin.route('/monetization/plan', methods=['POST'])
@admin_required
def save_plan():
    plan_id = request.form.get('plan_id')
    
    if plan_id:
        plan = PricingPlan.query.get(plan_id)
    else:
        plan = PricingPlan()
        db.session.add(plan)
    
    plan.name = request.form.get('name')
    plan.plan_type = request.form.get('plan_type')
    plan.price = float(request.form.get('price', 0))
    plan.currency = request.form.get('currency', 'USD')
    plan.duration_days = int(request.form.get('duration_days', 30)) if request.form.get('duration_days') else None
    plan.tokens_included = int(request.form.get('tokens_included', 0))
    plan.features = request.form.get('features', '[]')
    plan.is_active = request.form.get('is_active') == 'on'
    plan.is_featured = request.form.get('is_featured') == 'on'
    
    db.session.commit()
    log_action(session['admin_id'], 'save_pricing_plan', 'pricing_plan', plan.id)
    
    return redirect(url_for('admin.monetization'))

@admin.route('/monetization/promo', methods=['POST'])
@admin_required
def save_promo():
    promo = PromoCode(
        code=request.form.get('code').upper(),
        discount_type=request.form.get('discount_type'),
        discount_value=float(request.form.get('discount_value', 0)),
        max_uses=int(request.form.get('max_uses')) if request.form.get('max_uses') else None,
        is_active=True
    )
    
    if request.form.get('valid_from'):
        promo.valid_from = datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d')
    if request.form.get('valid_until'):
        promo.valid_until = datetime.strptime(request.form.get('valid_until'), '%Y-%m-%d')
    
    db.session.add(promo)
    db.session.commit()
    log_action(session['admin_id'], 'create_promo_code', 'promo_code', promo.id)
    
    return redirect(url_for('admin.monetization'))

@admin.route('/notifications')
@admin_required
def notifications():
    users = User.query.order_by(desc(User.created_at)).limit(100).all()
    sent_notifications = Notification.query.order_by(desc(Notification.created_at)).limit(50).all()
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/notifications.html',
                          users=users,
                          sent_notifications=sent_notifications,
                          admin_user=admin_user)

@admin.route('/notifications/send', methods=['POST'])
@admin_required
def send_notification():
    target = request.form.get('target')
    title = request.form.get('title')
    message = request.form.get('message')
    notification_type = request.form.get('notification_type', 'general')
    
    users = []
    if target == 'all':
        users = User.query.filter(User.is_active == True).all()
    elif target == 'vip':
        users = User.query.filter(User.is_vip == True).all()
    elif target == 'inactive':
        week_ago = datetime.utcnow() - timedelta(days=7)
        users = User.query.filter(db.or_(User.last_login < week_ago, User.last_login == None)).all()
    elif target == 'specific':
        user_ids = request.form.getlist('user_ids')
        users = User.query.filter(User.id.in_(user_ids)).all()
    
    for user in users:
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        db.session.add(notification)
    
    db.session.commit()
    log_action(session['admin_id'], 'send_notification', details=f'Target: {target}, Recipients: {len(users)}')
    
    return redirect(url_for('admin.notifications'))

@admin.route('/content')
@admin_required
def content():
    pages = ContentPage.query.order_by(ContentPage.title).all()
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/content.html', pages=pages, admin_user=admin_user)

@admin.route('/content/page', methods=['GET', 'POST'])
@admin_required
def edit_page():
    page_id = request.args.get('id')
    page = ContentPage.query.get(page_id) if page_id else None
    
    if request.method == 'POST':
        if not page:
            page = ContentPage()
            db.session.add(page)
        
        page.slug = request.form.get('slug')
        page.title = request.form.get('title')
        page.content = request.form.get('content')
        page.is_published = request.form.get('is_published') == 'on'
        page.updated_at = datetime.utcnow()
        page.updated_by = session['admin_id']
        
        db.session.commit()
        log_action(session['admin_id'], 'update_content_page', 'content_page', page.id)
        
        return redirect(url_for('admin.content'))
    
    admin_user = AdminUser.query.get(session['admin_id'])
    return render_template('admin/edit_page.html', page=page, admin_user=admin_user)

@admin.route('/security')
@admin_required
def security():
    admin_user = AdminUser.query.get(session['admin_id'])
    if admin_user.role != 'super_admin':
        return redirect(url_for('admin.dashboard'))
    
    admins = AdminUser.query.order_by(AdminUser.role, AdminUser.name).all()
    logs = AuditLog.query.order_by(desc(AuditLog.created_at)).limit(100).all()
    
    return render_template('admin/security.html', admins=admins, logs=logs, admin_user=admin_user)

@admin.route('/security/admin', methods=['POST'])
@admin_required
def manage_admin():
    admin_user = AdminUser.query.get(session['admin_id'])
    if admin_user.role != 'super_admin':
        return redirect(url_for('admin.dashboard'))
    
    action = request.form.get('action')
    
    if action == 'create':
        new_admin = AdminUser(
            email=request.form.get('email'),
            password_hash=generate_password_hash(request.form.get('password')),
            name=request.form.get('name'),
            role=request.form.get('role', 'moderator'),
            permissions=request.form.get('permissions', '[]')
        )
        db.session.add(new_admin)
        db.session.commit()
        log_action(session['admin_id'], 'create_admin', 'admin_user', new_admin.id)
    elif action == 'toggle':
        target_id = request.form.get('admin_id')
        target = AdminUser.query.get(target_id)
        if target and target.id != session['admin_id']:
            target.is_active = not target.is_active
            db.session.commit()
            log_action(session['admin_id'], 'toggle_admin_status', 'admin_user', target_id)
    
    return redirect(url_for('admin.security'))

@admin.route('/support')
@admin_required
def support():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = SupportTicket.query
    if status != 'all':
        query = query.filter(SupportTicket.status == status)
    
    tickets = query.order_by(desc(SupportTicket.created_at)).paginate(page=page, per_page=20)
    
    stats = {
        'open': SupportTicket.query.filter(SupportTicket.status == 'open').count(),
        'in_progress': SupportTicket.query.filter(SupportTicket.status == 'in_progress').count(),
        'resolved': SupportTicket.query.filter(SupportTicket.status == 'resolved').count()
    }
    
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/support.html', tickets=tickets, stats=stats, admin_user=admin_user)

@admin.route('/support/<int:ticket_id>', methods=['GET', 'POST'])
@admin_required
def ticket_detail(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'respond':
            response = TicketResponse(
                ticket_id=ticket_id,
                admin_id=session['admin_id'],
                message=request.form.get('message'),
                is_internal=request.form.get('is_internal') == 'on'
            )
            db.session.add(response)
            ticket.updated_at = datetime.utcnow()
            
            if not response.is_internal:
                notification = Notification(
                    user_id=ticket.user_id,
                    title='Réponse à votre ticket',
                    message=f'Votre ticket "{ticket.subject}" a reçu une réponse.',
                    notification_type='support',
                    action_url=f'/support/ticket/{ticket_id}'
                )
                db.session.add(notification)
        elif action == 'status':
            ticket.status = request.form.get('status')
            if ticket.status == 'resolved':
                ticket.resolved_at = datetime.utcnow()
            ticket.updated_at = datetime.utcnow()
        elif action == 'assign':
            ticket.assigned_to = session['admin_id']
            ticket.status = 'in_progress'
            ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        log_action(session['admin_id'], f'ticket_{action}', 'support_ticket', ticket_id)
        
        return redirect(url_for('admin.ticket_detail', ticket_id=ticket_id))
    
    responses = TicketResponse.query.filter(TicketResponse.ticket_id == ticket_id).order_by(TicketResponse.created_at).all()
    admin_user = AdminUser.query.get(session['admin_id'])
    
    return render_template('admin/ticket_detail.html', ticket=ticket, responses=responses, admin_user=admin_user)

@admin.route('/api/stats')
@admin_required
def api_stats():
    today = datetime.utcnow().date()
    
    return jsonify({
        'users_today': User.query.filter(func.date(User.created_at) == today).count(),
        'matches_today': Match.query.filter(func.date(Match.created_at) == today).count(),
        'messages_today': Message.query.filter(func.date(Message.created_at) == today).count(),
        'pending_reports': Report.query.filter(Report.status == 'pending').count()
    })
