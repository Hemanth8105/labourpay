from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, datetime
from extentions import db
from models import Employee, Attendance
from sqlalchemy.dialects.postgresql import insert

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance')
@login_required
def index():
    date_str = request.args.get('date', date.today().isoformat())
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()

    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()

    # Get existing attendance for this date
    att_map = {}
    existing = Attendance.query.filter_by(date=selected_date).all()
    for a in existing:
        att_map[a.employee_id] = a.status

    records = []
    for emp in employees:
        records.append({
            'id': emp.id,
            'name': emp.name,
            'daily_wage': float(emp.daily_wage),
            'status': att_map.get(emp.id, 'absent')
        })

    present = sum(1 for r in records if r['status'] == 'present')
    half = sum(1 for r in records if r['status'] == 'half_day')
    absent = sum(1 for r in records if r['status'] == 'absent')

    return render_template('pages/attendance.html',
        records=records,
        selected_date=selected_date,
        present=present, half=half, absent=absent
    )


@attendance_bp.route('/attendance/save', methods=['POST'])
@login_required
def save():
    date_str = request.form.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    employees = Employee.query.filter_by(is_active=True).all()

    for emp in employees:
        status = request.form.get(f'status_{emp.id}', 'absent')
        existing = Attendance.query.filter_by(employee_id=emp.id, date=selected_date).first()
        if existing:
            existing.status = status
        else:
            att = Attendance(employee_id=emp.id, date=selected_date, status=status)
            db.session.add(att)

    db.session.commit()
    flash('Attendance saved successfully!', 'success')
    return redirect(url_for('attendance.index', date=date_str))
