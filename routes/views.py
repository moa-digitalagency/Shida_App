from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def index():
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
    return render_template('app/home.html')

@views.route('/discovery')
@login_required
def discovery():
    return render_template('app/discovery.html')

@views.route('/negotiations')
@login_required
def negotiations():
    return render_template('app/negotiations.html')

@views.route('/chat/<int:match_id>')
@login_required
def chat(match_id):
    return render_template('app/chat.html', match_id=match_id)

@views.route('/profile')
@login_required
def profile():
    return render_template('app/profile.html')

@views.route('/market')
@login_required
def market():
    return render_template('app/market.html')

@views.route('/notifications')
@login_required
def notifications():
    return render_template('app/notifications.html')

@views.route('/settings')
@login_required
def settings():
    return render_template('app/settings.html')

@views.route('/page/<slug>')
def content_page(slug):
    from models import ContentPage
    page = ContentPage.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('app/content_page.html', page=page)
