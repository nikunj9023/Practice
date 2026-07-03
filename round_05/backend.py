from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'round05-secret-key'
CORS(app)

# ─── Mock Data ───────────────────────────────────────────────────────────────

users_db = {
    'admin': {
        'password': generate_password_hash('password'),
        'name': 'Admin User',
        'role': 'Admin'
    }
}

employees = [
    {"id": 1,  "first_name": "Nikunj",   "last_name": "Parmar",   "email": "nikunj@example.com",   "role": "Backend Developer",  "department": "Engineering"},
    {"id": 2,  "first_name": "Pratik",   "last_name": "Shah",     "email": "pratik@example.com",   "role": "Frontend Developer", "department": "Engineering"},
    {"id": 3,  "first_name": "Ankit",    "last_name": "Mehta",    "email": "ankit@example.com",    "role": "UI/UX Designer",     "department": "Product"},
    {"id": 4,  "first_name": "Sneha",    "last_name": "Patel",    "email": "sneha@example.com",    "role": "HR Manager",         "department": "Human Resources"},
    {"id": 5,  "first_name": "Rajan",    "last_name": "Verma",    "email": "rajan@example.com",    "role": "DevOps Engineer",    "department": "Infrastructure"},
    {"id": 6,  "first_name": "Pooja",    "last_name": "Sharma",   "email": "pooja@example.com",    "role": "QA Engineer",        "department": "Quality"},
    {"id": 7,  "first_name": "Vikram",   "last_name": "Singh",    "email": "vikram@example.com",   "role": "Project Manager",    "department": "Management"},
    {"id": 8,  "first_name": "Divya",    "last_name": "Gupta",    "email": "divya@example.com",    "role": "Data Analyst",       "department": "Analytics"},
    {"id": 9,  "first_name": "Rohit",    "last_name": "Joshi",    "email": "rohit@example.com",    "role": "Mobile Developer",   "department": "Engineering"},
    {"id": 10, "first_name": "Priya",    "last_name": "Nair",     "email": "priya@example.com",    "role": "Business Analyst",   "department": "Strategy"},
    {"id": 11, "first_name": "Karan",    "last_name": "Malhotra", "email": "karan@example.com",    "role": "Security Engineer",  "department": "Infrastructure"},
    {"id": 12, "first_name": "Neha",     "last_name": "Desai",    "email": "neha@example.com",     "role": "Content Writer",     "department": "Marketing"},
]

# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def make_access_token(username):
    return jwt.encode(
        {'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        app.config['SECRET_KEY'], algorithm='HS256'
    )

def make_refresh_token(username):
    return jwt.encode(
        {'user': username, 'type': 'refresh', 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        app.config['SECRET_KEY'], algorithm='HS256'
    )

def verify_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    user = users_db.get(username)
    if user and check_password_hash(user['password'], password):
        access_token = make_access_token(username)
        refresh_token = make_refresh_token(username)
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {'username': username, 'name': user['name'], 'role': user['role']}
        })

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    payload = verify_token(token)

    if not payload or payload.get('type') != 'refresh':
        return jsonify({'message': 'Invalid or expired refresh token'}), 401

    new_access_token = make_access_token(payload['user'])
    return jsonify({'access_token': new_access_token})

# ─── Employees Routes ─────────────────────────────────────────────────────────

@app.route('/api/employees', methods=['GET'])
def get_employees():
    search = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Filter by search term
    filtered = [
        e for e in employees
        if search in e['first_name'].lower()
        or search in e['last_name'].lower()
        or search in e['email'].lower()
        or search in e['department'].lower()
    ] if search else employees[:]

    total = len(filtered)
    total_pages = max(1, -(-total // limit))  # ceiling division
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    return jsonify({
        'data': paginated,
        'total': total,
        'current_page': page,
        'total_pages': total_pages
    })


@app.route('/api/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    emp = next((e for e in employees if e['id'] == emp_id), None)
    if emp:
        return jsonify(emp)
    return jsonify({'error': 'Employee not found'}), 404


@app.route('/api/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    new_id = max(e['id'] for e in employees) + 1
    new_emp = {
        'id': new_id,
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
        'email': data.get('email', ''),
        'role': data.get('role', ''),
        'department': data.get('department', ''),
    }
    employees.append(new_emp)
    return jsonify(new_emp), 201


@app.route('/api/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    global employees
    emp = next((e for e in employees if e['id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    employees = [e for e in employees if e['id'] != emp_id]
    return jsonify({'message': f'Employee {emp_id} deleted successfully'})


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("✅  Flask backend running at http://127.0.0.1:5000")
    print("   Endpoints:")
    print("   POST /api/auth/login")
    print("   POST /api/auth/refresh")
    print("   GET  /api/employees?search=&page=1&limit=10")
    print("   POST /api/employees")
    print("   DELETE /api/employees/<id>")
    app.run(debug=True, port=5000)
