from extentions import db
from flask_login import UserMixin
from datetime import date


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    daily_wage = db.Column(db.Numeric(10, 2), nullable=False)
    joining_date = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    attendance = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete')
    advances = db.relationship('Advance', backref='employee', lazy=True, cascade='all, delete')


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='absent')  # present, absent, half_day
    __table_args__ = (db.UniqueConstraint('employee_id', 'date'),)


class Advance(db.Model):
    __tablename__ = 'advances'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, default=date.today)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Payroll(db.Model):
    __tablename__ = 'payroll'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    present_days = db.Column(db.Numeric(5, 1), default=0)
    daily_wage = db.Column(db.Numeric(10, 2), nullable=False)
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False)
    advance_deduction = db.Column(db.Numeric(10, 2), default=0)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (db.UniqueConstraint('employee_id', 'month', 'year'),)
