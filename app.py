import os
import logging
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, 
    static_folder='statics',
    template_folder='templates'
)

app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    app.secret_key = 'dev-secret-key-change-in-production'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

from models import db
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'views.index'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

from routes.api import api
from routes.views import views
from routes.admin import admin

app.register_blueprint(api)
app.register_blueprint(views)
app.register_blueprint(admin)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

with app.app_context():
    import models as m
    db.create_all()
    
    from data.init_db import init_database
    init_database(db, m)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
