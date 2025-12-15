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
