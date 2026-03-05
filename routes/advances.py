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

    advances = db.session.query(Advance, Employee.name).join(Employee).filter(
        func.extract('month', Advance.date) == month,
        func.extract('year', Advance.date) == year
    ).order_by(Advance.date.desc()).all()

    total = sum(float(a.Advance.amount) for a in advances)
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()

    # Build month/year options for dropdown
    months = [{'value': i, 'label': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)]

    return render_template('pages/advances.html',
        advances=advances,
        total=total,
        employees=employees,
        selected_month=month,
        selected_year=year,
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

    adv = Advance(employee_id=employee_id, amount=amount, date=adv_date, note=note)
    db.session.add(adv)
    db.session.commit()
    flash('Advance recorded!', 'success')
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
