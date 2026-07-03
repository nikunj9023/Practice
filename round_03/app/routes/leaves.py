from flask import Blueprint, jsonify, request
from datetime import date as dt_date, timedelta
import random

leaves_bp = Blueprint('leaves', __name__, url_prefix='/api')

# ─── Employee roster ──────────────────────────────────────────────────────────

_employees = {
    1:  {"first_name": "Nikunj",  "last_name": "Parmar",   "department": "Engineering"},
    2:  {"first_name": "Pratik",  "last_name": "Shah",     "department": "Engineering"},
    3:  {"first_name": "Ankit",   "last_name": "Mehta",    "department": "Product"},
    4:  {"first_name": "Sneha",   "last_name": "Patel",    "department": "Human Resources"},
    5:  {"first_name": "Rajan",   "last_name": "Verma",    "department": "Infrastructure"},
    6:  {"first_name": "Pooja",   "last_name": "Sharma",   "department": "Quality"},
    7:  {"first_name": "Vikram",  "last_name": "Singh",    "department": "Management"},
    8:  {"first_name": "Divya",   "last_name": "Gupta",    "department": "Analytics"},
    9:  {"first_name": "Rohit",   "last_name": "Joshi",    "department": "Engineering"},
    10: {"first_name": "Priya",   "last_name": "Nair",     "department": "Strategy"},
    11: {"first_name": "Karan",   "last_name": "Malhotra", "department": "Infrastructure"},
    12: {"first_name": "Neha",    "last_name": "Desai",    "department": "Marketing"},
}

LEAVE_TYPES = ['Sick Leave', 'Casual Leave', 'Earned Leave', 'Maternity Leave', 'Unpaid Leave']
STATUSES    = ['Pending', 'Approved', 'Rejected']

# ─── Seed mock leave data ─────────────────────────────────────────────────────

def _random_date_range():
    base  = dt_date.today() - timedelta(days=random.randint(1, 30))
    days  = random.randint(1, 5)
    return str(base), str(base + timedelta(days=days - 1))

_leaves = []
_next_id = 1

def _seed():
    global _next_id
    sample_reasons = [
        'Feeling unwell', 'Family function', 'Personal work',
        'Medical appointment', 'Vacation', 'Home emergency', ''
    ]
    for emp_id in random.sample(list(_employees.keys()), 8):
        from_d, to_d = _random_date_range()
        _leaves.append({
            'id':         _next_id,
            'employee_id': emp_id,
            'first_name': _employees[emp_id]['first_name'],
            'last_name':  _employees[emp_id]['last_name'],
            'department': _employees[emp_id]['department'],
            'leave_type': random.choice(LEAVE_TYPES),
            'from_date':  from_d,
            'to_date':    to_d,
            'reason':     random.choice(sample_reasons),
            'status':     random.choice(STATUSES),
            'applied_on': str(dt_date.today()),
        })
        _next_id += 1

_seed()

# ─── Routes ───────────────────────────────────────────────────────────────────

@leaves_bp.route('/leaves', methods=['GET'])
def get_leaves():
    status = request.args.get('status')
    result = _leaves if not status else [l for l in _leaves if l['status'] == status]
    # newest first
    return jsonify(list(reversed(result)))


@leaves_bp.route('/leaves/<int:leave_id>', methods=['GET'])
def get_leave(leave_id):
    leave = next((l for l in _leaves if l['id'] == leave_id), None)
    if not leave:
        return jsonify({'error': 'Leave request not found'}), 404
    return jsonify(leave)


@leaves_bp.route('/leaves', methods=['POST'])
def create_leave():
    global _next_id
    data       = request.get_json()
    emp_id     = int(data.get('employee_id', 0))
    leave_type = data.get('leave_type', LEAVE_TYPES[0])
    from_date  = data.get('from_date')
    to_date    = data.get('to_date')
    reason     = data.get('reason', '')

    if emp_id not in _employees:
        return jsonify({'error': f'Employee {emp_id} not found'}), 404
    if not from_date or not to_date:
        return jsonify({'error': 'from_date and to_date are required'}), 400
    if from_date > to_date:
        return jsonify({'error': 'from_date must be before to_date'}), 400

    emp = _employees[emp_id]
    new_leave = {
        'id':          _next_id,
        'employee_id': emp_id,
        'first_name':  emp['first_name'],
        'last_name':   emp['last_name'],
        'department':  emp['department'],
        'leave_type':  leave_type,
        'from_date':   from_date,
        'to_date':     to_date,
        'reason':      reason,
        'status':      'Pending',
        'applied_on':  str(dt_date.today()),
    }
    _leaves.append(new_leave)
    _next_id += 1
    return jsonify(new_leave), 201


@leaves_bp.route('/leaves/<int:leave_id>', methods=['PATCH'])
def update_leave_status(leave_id):
    data   = request.get_json()
    status = data.get('status')

    if status not in STATUSES:
        return jsonify({'error': f'Invalid status. Must be one of: {STATUSES}'}), 400

    leave = next((l for l in _leaves if l['id'] == leave_id), None)
    if not leave:
        return jsonify({'error': 'Leave request not found'}), 404

    leave['status'] = status
    return jsonify(leave)


@leaves_bp.route('/leaves/<int:leave_id>', methods=['DELETE'])
def delete_leave(leave_id):
    global _leaves
    leave = next((l for l in _leaves if l['id'] == leave_id), None)
    if not leave:
        return jsonify({'error': 'Leave request not found'}), 404
    _leaves = [l for l in _leaves if l['id'] != leave_id]
    return jsonify({'message': f'Leave request {leave_id} deleted'})
