from flask import Blueprint, render_template
from flask_login import login_required
from datetime import date
from models import Employee, Attendance, Advance
from extentions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    total_employees = Employee.query.filter_by(is_active=True).count()

    today_att = Attendance.query.filter_by(date=today).all()
    present_today = sum(1 for a in today_att if a.status in ('present', 'half_day'))
    absent_today = sum(1 for a in today_att if a.status == 'absent')

    month_advances = db.session.query(func.sum(Advance.amount)).filter(
        func.extract('month', Advance.date) == today.month,
        func.extract('year', Advance.date) == today.year
    ).scalar() or 0

    return render_template('pages/dashboard.html',
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        month_advances=float(month_advances),
        today=today
    )
