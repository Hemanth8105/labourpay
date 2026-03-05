from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, datetime
from extentions import db
from models import Advance, Employee
from sqlalchemy import func

advances_bp = Blueprint('advances', __name__)


@advances_bp.route('/advances')
@login_required
def index():
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    employee_filter = request.args.get('employee_id', '')

    query = db.session.query(Advance, Employee.name).join(Employee).filter(
        func.extract('month', Advance.date) == month,
        func.extract('year', Advance.date) == year
    )

    if employee_filter:
        query = query.filter(Advance.employee_id == int(employee_filter))

    advances = query.order_by(Advance.date.desc()).all()
    total = sum(float(a.Advance.amount) for a in advances)
    total_recovered = sum(float(a.Advance.recovered or 0) for a in advances)
    total_remaining = total - total_recovered

    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    months = [{'value': i, 'label': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)]

    return render_template('pages/advances.html',
        advances=advances,
        total=total,
        total_recovered=total_recovered,
        total_remaining=total_remaining,
        employees=employees,
        selected_month=month,
        selected_year=year,
        selected_employee=employee_filter,
        months=months,
        current_year=today.year
    )


@advances_bp.route('/advances/add', methods=['POST'])
@login_required
def add():
    employee_id = request.form.get('employee_id')
    amount = request.form.get('amount')
    adv_date = request.form.get('date') or date.today()
    note = request.form.get('note', '').strip()
    month = request.form.get('month', date.today().month)
    year = request.form.get('year', date.today().year)

    if not employee_id or not amount:
        flash('Employee and amount are required.', 'error')
        return redirect(url_for('advances.index', month=month, year=year))

    adv = Advance(employee_id=employee_id, amount=amount, date=adv_date, note=note, recovered=0)
    db.session.add(adv)
    db.session.commit()
    flash('Advance recorded!', 'success')
    return redirect(url_for('advances.index', month=month, year=year))


@advances_bp.route('/advances/recover/<int:adv_id>', methods=['POST'])
@login_required
def recover(adv_id):
    adv = Advance.query.get_or_404(adv_id)
    recover_amount = float(request.form.get('recover_amount', 0))
    month = adv.date.month
    year = adv.date.year

    current_recovered = float(adv.recovered or 0)
    remaining = float(adv.amount) - current_recovered

    if recover_amount <= 0:
        flash('Recovery amount must be greater than 0.', 'error')
        return redirect(url_for('advances.index', month=month, year=year))

    if recover_amount > remaining:
        flash(f'Cannot recover more than remaining balance ₹{remaining:,.0f}.', 'error')
        return redirect(url_for('advances.index', month=month, year=year))

    adv.recovered = current_recovered + recover_amount
    db.session.commit()
    new_remaining = float(adv.amount) - float(adv.recovered)
    flash(f'₹{recover_amount:,.0f} recovered! Remaining balance: ₹{new_remaining:,.0f}', 'success')
    return redirect(url_for('advances.index', month=month, year=year))


@advances_bp.route('/advances/delete/<int:adv_id>', methods=['POST'])
@login_required
def delete(adv_id):
    adv = Advance.query.get_or_404(adv_id)
    month = adv.date.month
    year = adv.date.year
    db.session.delete(adv)
    db.session.commit()
    flash('Advance deleted.', 'success')
    return redirect(url_for('advances.index', month=month, year=year))
