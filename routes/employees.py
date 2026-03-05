from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extentions import db
from models import Employee
from datetime import date

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/employees')
@login_required
def index():
    category = request.args.get('category', 'all')
    query = Employee.query.filter_by(is_active=True)

    # Order: masons first, then female, then male
    if category == 'mason':
        employees = query.filter_by(category='mason').order_by(Employee.name).all()
    elif category == 'female':
        employees = query.filter_by(category='female').order_by(Employee.name).all()
    elif category == 'male':
        employees = query.filter_by(category='male').order_by(Employee.name).all()
    else:
        # All: masons first, then female, then male
        masons = query.filter_by(category='mason').order_by(Employee.name).all()
        females = query.filter_by(category='female').order_by(Employee.name).all()
        males = query.filter_by(category='male').order_by(Employee.name).all()
        employees = masons + females + males

    return render_template('pages/employees.html', employees=employees, active_category=category)


@employees_bp.route('/employees/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    daily_wage = request.form.get('daily_wage')
    joining_date = request.form.get('joining_date') or date.today()
    category = request.form.get('category', 'male')

    if not name or not daily_wage:
        flash('Name and daily wage are required.', 'error')
        return redirect(url_for('employees.index'))

    emp = Employee(name=name, phone=phone, daily_wage=daily_wage, joining_date=joining_date, category=category)
    db.session.add(emp)
    db.session.commit()
    flash(f'{name} added successfully!', 'success')
    return redirect(url_for('employees.index'))


@employees_bp.route('/employees/edit/<int:emp_id>', methods=['POST'])
@login_required
def edit(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    emp.name = request.form.get('name', emp.name).strip()
    emp.phone = request.form.get('phone', '').strip()
    emp.daily_wage = request.form.get('daily_wage', emp.daily_wage)
    emp.category = request.form.get('category', emp.category)
    db.session.commit()
    flash('Employee updated.', 'success')
    return redirect(url_for('employees.index'))


@employees_bp.route('/employees/delete/<int:emp_id>', methods=['POST'])
@login_required
def delete(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    emp.is_active = False
    db.session.commit()
    flash(f'{emp.name} removed.', 'success')
    return redirect(url_for('employees.index'))
