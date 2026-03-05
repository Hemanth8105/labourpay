from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
import bcrypt
from extentions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            login_user(user, remember=True)
            return redirect(url_for('dashboard.index'))
        flash('Invalid username or password.', 'error')
    return render_template('pages/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Username and password are required.', 'error')
        else:
            # Check if username already taken
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already taken. Please choose another.', 'error')
            else:
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                user = User(username=username, password=hashed)
                db.session.add(user)
                db.session.commit()
                flash('Account created! Please login.', 'success')
                return redirect(url_for('auth.login'))
    return render_template('pages/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
