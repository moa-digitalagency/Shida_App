from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

BREADCRUMB_MAP = {
    'home': {'label': 'Accueil', 'parent': None},
    'discovery': {'label': 'Explorer', 'parent': None},
    'negotiations': {'label': 'Négociation', 'parent': 'home'},
    'chat': {'label': 'Conversation', 'parent': 'negotiations'},
    'profile': {'label': 'Profil', 'parent': 'home'},
    'settings': {'label': 'Paramètres', 'parent': 'profile'},
    'market': {'label': 'Boutique', 'parent': 'home'},
    'notifications': {'label': 'Alertes', 'parent': 'home'},
}

def get_breadcrumbs(page_key, extra_label=None):
    breadcrumbs = []
    current = page_key
    while current:
        page_info = BREADCRUMB_MAP.get(current, {})
        label = extra_label if extra_label and current == page_key else page_info.get('label', current)
        breadcrumbs.insert(0, {'label': label, 'url': url_for(f'views.{current}') if current != 'chat' else '#'})
        current = page_info.get('parent')
    return breadcrumbs

@views.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    return redirect(url_for('views.discovery'))

@views.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    return render_template('auth/login.html')

@views.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    return render_template('auth/register.html')

@views.route('/home')
@login_required
def home():
    return render_template('app/home.html', breadcrumbs=get_breadcrumbs('home'))

@views.route('/discovery')
def discovery():
    return render_template('app/discovery.html', is_guest=not current_user.is_authenticated, breadcrumbs=get_breadcrumbs('discovery'))

@views.route('/negotiations')
@login_required
def negotiations():
    return render_template('app/negotiations.html', breadcrumbs=get_breadcrumbs('negotiations'))

@views.route('/chat/<int:match_id>')
@login_required
def chat(match_id):
    return render_template('app/chat.html', match_id=match_id, breadcrumbs=get_breadcrumbs('chat'))

@views.route('/profile')
@login_required
def profile():
    return render_template('app/profile.html', breadcrumbs=get_breadcrumbs('profile'))

@views.route('/market')
def market():
    return render_template('app/market.html', is_guest=not current_user.is_authenticated, breadcrumbs=get_breadcrumbs('market'))

@views.route('/notifications')
@login_required
def notifications():
    return render_template('app/notifications.html', breadcrumbs=get_breadcrumbs('notifications'))

@views.route('/settings')
@login_required
def settings():
    return render_template('app/settings.html', breadcrumbs=get_breadcrumbs('settings'))

@views.route('/page/<slug>')
def content_page(slug):
    from models import ContentPage
    page = ContentPage.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('app/content_page.html', page=page)
