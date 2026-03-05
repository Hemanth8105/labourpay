# LabourPay (Python Version)
Daily Labour Management System — Flask + PostgreSQL + Jinja2

---

## Features
- 👷 Employee Management — Add/edit/remove labourers with daily wage
- 📅 Daily Attendance — Mark Present / Half Day / Absent
- 💰 Advance Tracking — Record advances, auto-deducted in payroll
- 🧮 Auto Payroll Calculation — Gross & net salary calculated automatically
- 📄 Salary Slip — View & print per employee
- 📊 Excel Export — Download payroll + attendance as .xlsx
- 🔐 Secure Login — Single owner account
- 📱 Responsive — Works on mobile & desktop

---

## Tech Stack
- **Backend + Frontend**: Python / Flask
- **Templates**: Jinja2 HTML
- **Database**: PostgreSQL + SQLAlchemy
- **Auth**: Flask-Login + bcrypt
- **Excel**: openpyxl

---

## Setup Instructions

### Step 1 — Install PostgreSQL
Download from postgresql.org, install and start it.

Then create the database:
```sql
CREATE DATABASE labour_payroll;
```

### Step 2 — Install Python dependencies
```bash
cd labourpay-python

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3 — Configure environment
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and set your values:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/labour_payroll
SECRET_KEY=any_long_random_string_here
```

### Step 4 — Run the app
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

### Step 5 — First Time Setup
1. Click **"First time? Create account"**
2. Set your username and password
3. Login and start using!

---

## Payroll Calculation
```
Effective Days = Present Days + (Half Days × 0.5)
Gross Salary   = Effective Days × Daily Wage
Net Salary     = Gross Salary − Advance Deductions
```

---

## Project Structure
```
labourpay-python/
├── app.py                  # Flask app factory & entry point
├── models.py               # SQLAlchemy database models
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Login & register
│   ├── dashboard.py        # Dashboard stats
│   ├── employees.py        # Labourer CRUD
│   ├── attendance.py       # Daily attendance
│   ├── advances.py         # Advance payments
│   └── payroll.py          # Payroll + Excel export
├── templates/
│   ├── base.html           # Layout with sidebar
│   └── pages/
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── employees.html
│       ├── attendance.html
│       ├── advances.html
│       └── payroll.html
└── static/
    ├── css/main.css        # Full design system
    └── js/main.js          # Modal & flash handling
```

---

## Excel Export
Go to **Payroll** → Select month & year → Click **Export Excel**

Exports two sheets:
- **Payroll sheet** — All employees with wage, days, gross, advance, net salary
- **Attendance sheet** — Full daily attendance log for the month
