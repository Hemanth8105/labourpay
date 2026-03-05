from flask import Flask
from extentions import db, login_manager
from dotenv import load_dotenv
import os

load_dotenv()



def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_change_this')

    # Fix for Railway's postgres:// URL (SQLAlchemy requires postgresql://)
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/labour_payroll')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to continue.'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.employees import employees_bp
    from routes.attendance import attendance_bp
    from routes.advances import advances_bp
    from routes.payroll import payroll_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(advances_bp)
    app.register_blueprint(payroll_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
