from flask import Blueprint, jsonify, request

employees_bp = Blueprint('employees', __name__, url_prefix='/api')

# ─── Mock Employee Data ───────────────────────────────────────────────────────

_employees = [
    {"id": 1,  "first_name": "Nikunj",  "last_name": "Parmar",   "email": "nikunj@example.com",  "role": "Backend Developer",  "department": "Engineering"},
    {"id": 2,  "first_name": "Pratik",  "last_name": "Shah",     "email": "pratik@example.com",  "role": "Frontend Developer", "department": "Engineering"},
    {"id": 3,  "first_name": "Ankit",   "last_name": "Mehta",    "email": "ankit@example.com",   "role": "UI/UX Designer",     "department": "Product"},
    {"id": 4,  "first_name": "Sneha",   "last_name": "Patel",    "email": "sneha@example.com",   "role": "HR Manager",         "department": "Human Resources"},
    {"id": 5,  "first_name": "Rajan",   "last_name": "Verma",    "email": "rajan@example.com",   "role": "DevOps Engineer",    "department": "Infrastructure"},
    {"id": 6,  "first_name": "Pooja",   "last_name": "Sharma",   "email": "pooja@example.com",   "role": "QA Engineer",        "department": "Quality"},
    {"id": 7,  "first_name": "Vikram",  "last_name": "Singh",    "email": "vikram@example.com",  "role": "Project Manager",    "department": "Management"},
    {"id": 8,  "first_name": "Divya",   "last_name": "Gupta",    "email": "divya@example.com",   "role": "Data Analyst",       "department": "Analytics"},
    {"id": 9,  "first_name": "Rohit",   "last_name": "Joshi",    "email": "rohit@example.com",   "role": "Mobile Developer",   "department": "Engineering"},
    {"id": 10, "first_name": "Priya",   "last_name": "Nair",     "email": "priya@example.com",   "role": "Business Analyst",   "department": "Strategy"},
    {"id": 11, "first_name": "Karan",   "last_name": "Malhotra", "email": "karan@example.com",   "role": "Security Engineer",  "department": "Infrastructure"},
    {"id": 12, "first_name": "Neha",    "last_name": "Desai",    "email": "neha@example.com",    "role": "Content Writer",     "department": "Marketing"},
]


# ─── Routes ───────────────────────────────────────────────────────────────────

@employees_bp.route('/employees', methods=['GET'])
def get_employees():
    search = request.args.get('search', '').lower()
    page  = request.args.get('page',  1, type=int)
    limit = request.args.get('limit', 10, type=int)

    filtered = [
        e for e in _employees
        if search in e['first_name'].lower()
        or search in e['last_name'].lower()
        or search in e['email'].lower()
        or search in e['department'].lower()
    ] if search else _employees[:]

    total       = len(filtered)
    total_pages = max(1, -(-total // limit))   # ceiling division
    start       = (page - 1) * limit
    paginated   = filtered[start: start + limit]

    return jsonify({
        'data':         paginated,
        'total':        total,
        'current_page': page,
        'total_pages':  total_pages,
    })


@employees_bp.route('/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    emp = next((e for e in _employees if e['id'] == emp_id), None)
    if emp:
        return jsonify(emp)
    return jsonify({'error': 'Employee not found'}), 404


@employees_bp.route('/employees', methods=['POST'])
def create_employee():
    data    = request.get_json()
    new_id  = max(e['id'] for e in _employees) + 1
    new_emp = {
        'id':         new_id,
        'first_name': data.get('first_name', ''),
        'last_name':  data.get('last_name',  ''),
        'email':      data.get('email',      ''),
        'role':       data.get('role',       ''),
        'department': data.get('department', ''),
    }
    _employees.append(new_emp)
    return jsonify(new_emp), 201


@employees_bp.route('/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    global _employees
    emp = next((e for e in _employees if e['id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    _employees = [e for e in _employees if e['id'] != emp_id]
    return jsonify({'message': f'Employee {emp_id} deleted successfully'})
