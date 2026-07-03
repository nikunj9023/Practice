from flask import Blueprint, jsonify, request
import random
from datetime import date as dt_date

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api')

# ─── Employee roster (mirrors employees.py) ──────────────────────────────────

_employees = [
    {"id": 1,  "first_name": "Nikunj",  "last_name": "Parmar",   "role": "Backend Developer",  "department": "Engineering"},
    {"id": 2,  "first_name": "Pratik",  "last_name": "Shah",     "role": "Frontend Developer", "department": "Engineering"},
    {"id": 3,  "first_name": "Ankit",   "last_name": "Mehta",    "role": "UI/UX Designer",     "department": "Product"},
    {"id": 4,  "first_name": "Sneha",   "last_name": "Patel",    "role": "HR Manager",         "department": "Human Resources"},
    {"id": 5,  "first_name": "Rajan",   "last_name": "Verma",    "role": "DevOps Engineer",    "department": "Infrastructure"},
    {"id": 6,  "first_name": "Pooja",   "last_name": "Sharma",   "role": "QA Engineer",        "department": "Quality"},
    {"id": 7,  "first_name": "Vikram",  "last_name": "Singh",    "role": "Project Manager",    "department": "Management"},
    {"id": 8,  "first_name": "Divya",   "last_name": "Gupta",    "role": "Data Analyst",       "department": "Analytics"},
    {"id": 9,  "first_name": "Rohit",   "last_name": "Joshi",    "role": "Mobile Developer",   "department": "Engineering"},
    {"id": 10, "first_name": "Priya",   "last_name": "Nair",     "role": "Business Analyst",   "department": "Strategy"},
    {"id": 11, "first_name": "Karan",   "last_name": "Malhotra", "role": "Security Engineer",  "department": "Infrastructure"},
    {"id": 12, "first_name": "Neha",    "last_name": "Desai",    "role": "Content Writer",     "department": "Marketing"},
]

# In-memory attendance store: { "YYYY-MM-DD": { employee_id: status } }
_attendance: dict[str, dict[int, str]] = {}

_STATUSES = ['Present', 'Absent', 'Half Day', 'On Leave']


def _default_status():
    """Randomly generate a realistic status for seed data."""
    weights = [70, 15, 10, 5]          # % probability
    return random.choices(_STATUSES, weights=weights, k=1)[0]


def _seed_date(date_str: str):
    """Auto-generate attendance for all employees for a given date if not yet set."""
    if date_str not in _attendance:
        _attendance[date_str] = {
            emp['id']: _default_status() for emp in _employees
        }


# ─── Routes ───────────────────────────────────────────────────────────────────

@attendance_bp.route('/attendance', methods=['GET'])
def get_attendance():
    date_str = request.args.get('date', str(dt_date.today()))
    _seed_date(date_str)

    daily = _attendance[date_str]
    result = []
    for emp in _employees:
        result.append({
            'employee_id': emp['id'],
            'first_name':  emp['first_name'],
            'last_name':   emp['last_name'],
            'role':        emp['role'],
            'department':  emp['department'],
            'status':      daily.get(emp['id'], 'Absent'),
            'date':        date_str,
        })

    return jsonify(result)


@attendance_bp.route('/attendance', methods=['POST'])
def mark_attendance():
    data        = request.get_json()
    employee_id = data.get('employee_id')
    date_str    = data.get('date', str(dt_date.today()))
    status      = data.get('status')

    if status not in _STATUSES:
        return jsonify({'error': f'Invalid status. Must be one of: {_STATUSES}'}), 400

    _seed_date(date_str)
    _attendance[date_str][employee_id] = status

    return jsonify({
        'employee_id': employee_id,
        'date':        date_str,
        'status':      status,
        'message':     'Attendance updated successfully',
    })
