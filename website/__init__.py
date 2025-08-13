from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User
from werkzeug.security import generate_password_hash

def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
    return response


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'myvehicleapp2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.after_request(add_header)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')

    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
        create_admin()  

    return app

def create_admin():
    admin_email = 'admin@vplot.com'
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            name='Admin',
            email=admin_email,
            password=generate_password_hash('admin123'),  # default password
            is_admin=True,
            role='admin'

        )
        db.session.add(admin)
        db.session.commit()