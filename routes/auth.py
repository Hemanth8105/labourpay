from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
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


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
        elif new_password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        else:
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('No account found with that username.', 'error')
            else:
                hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                user.password = hashed
                db.session.commit()
                flash('Password reset successfully! Please login.', 'success')
                return redirect(url_for('auth.login'))

    return render_template('pages/forgot_password.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
        elif not bcrypt.checkpw(current_password.encode(), current_user.password.encode()):
            flash('Current password is incorrect.', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'error')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'error')
        elif current_password == new_password:
            flash('New password must be different from current password.', 'error')
        else:
            # Query fresh from DB to avoid Flask-Login proxy issue
            user = User.query.get(current_user.id)
            hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            user.password = hashed
            db.session.add(user)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('pages/change_password.html')
