from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, datetime
from extentions import db
from models import Employee, Attendance
import calendar

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance')
@login_required
def index():
    today = date.today()

    # Daily view date
    date_str = request.args.get('date', today.isoformat())
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    # Grid view month/year
    grid_month = int(request.args.get('grid_month', today.month))
    grid_year = int(request.args.get('grid_year', today.year))

    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()

    # --- Daily view data ---
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

    # --- Grid view data ---
    num_days = calendar.monthrange(grid_year, grid_month)[1]
    grid_days = [date(grid_year, grid_month, d) for d in range(1, num_days + 1)]

    # Get all attendance for this month
    all_att = Attendance.query.filter(
        Attendance.date >= date(grid_year, grid_month, 1),
        Attendance.date <= date(grid_year, grid_month, num_days)
    ).all()

    # Build map: {employee_id: {date: status}}
    att_grid_map = {}
    for a in all_att:
        if a.employee_id not in att_grid_map:
            att_grid_map[a.employee_id] = {}
        att_grid_map[a.employee_id][a.date] = a.status

    grid_data = []
    for emp in employees:
        emp_att = att_grid_map.get(emp.id, {})
        p = sum(1 for d in grid_days if emp_att.get(d) == 'present')
        h = sum(1 for d in grid_days if emp_att.get(d) == 'half_day')
        ab = sum(1 for d in grid_days if emp_att.get(d, 'absent') == 'absent')
        eff = p + h * 0.5
        grid_data.append({
            'id': emp.id,
            'name': emp.name,
            'days': emp_att,
            'present': p,
            'half': h,
            'absent': ab,
            'effective': eff,
        })

    grid_months = [{'value': i, 'label': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)]

    return render_template('pages/attendance.html',
        records=records,
        selected_date=selected_date,
        present=present, half=half, absent=absent,
        grid_data=grid_data,
        grid_days=grid_days,
        grid_selected_month=grid_month,
        grid_selected_year=grid_year,
        grid_months=grid_months,
        grid_current_year=today.year,
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


@attendance_bp.route('/attendance/employee/<int:emp_id>')
@login_required
def employee_view(emp_id):
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))

    employee = Employee.query.get_or_404(emp_id)
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()

    num_days = calendar.monthrange(year, month)[1]
    all_days = [date(year, month, d) for d in range(1, num_days + 1)]

    att_records = Attendance.query.filter(
        Attendance.employee_id == emp_id,
        Attendance.date >= date(year, month, 1),
        Attendance.date <= date(year, month, num_days)
    ).all()

    att_map = {a.date: a.status for a in att_records}

    day_records = []
    for d in all_days:
        status = att_map.get(d, 'absent')
        day_records.append({
            'date': d,
            'day_name': d.strftime('%A'),
            'status': status
        })

    present = sum(1 for r in day_records if r['status'] == 'present')
    half = sum(1 for r in day_records if r['status'] == 'half_day')
    absent = sum(1 for r in day_records if r['status'] == 'absent')
    effective = present + half * 0.5

    months = [{'value': i, 'label': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)]

    return render_template('pages/attendance_employee.html',
        employee=employee,
        employees=employees,
        day_records=day_records,
        present=present, half=half, absent=absent,
        effective=effective,
        selected_month=month,
        selected_year=year,
        month_name=datetime(year, month, 1).strftime('%B'),
        months=months,
        current_year=today.year
    )
