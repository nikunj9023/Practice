from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import base64
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'round05-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max upload
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

attendance_db = []
leaves_db = []



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


@app.route('/api/employees/<int:emp_id>/upload-image', methods=['POST'])
def upload_employee_image(emp_id):
    emp = next((e for e in employees if e['id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    image_data = data['image']  # Expects a base64 data URL: "data:image/png;base64,..."
    if not image_data.startswith('data:image/'):
        return jsonify({'error': 'Invalid image format. Must be a base64 data URL.'}), 400

    emp['profile_image_url'] = image_data
    return jsonify({'message': 'Image uploaded successfully', 'profile_image_url': image_data})

# ─── Attendance Routes ────────────────────────────────────────────────────────

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    date = request.args.get('date', '')
    if not date:
        return jsonify({'error': 'Date is required'}), 400
        
    result = []
    for emp in employees:
        record = next((r for r in attendance_db if r['employee_id'] == emp['id'] and r['date'] == date), None)
        status = record['status'] if record else 'Absent'
        
        result.append({
            'employee_id': emp['id'],
            'first_name': emp['first_name'],
            'last_name': emp['last_name'],
            'role': emp['role'],
            'department': emp['department'],
            'status': status,
            'date': date
        })
        
    return jsonify(result)

@app.route('/api/attendance', methods=['POST'])
def update_attendance():
    data = request.get_json()
    emp_id = data.get('employee_id')
    date = data.get('date')
    status = data.get('status')
    
    if not emp_id or not date or not status:
        return jsonify({'error': 'Missing data'}), 400
        
    record = next((r for r in attendance_db if r['employee_id'] == emp_id and r['date'] == date), None)
    if record:
        record['status'] = status
    else:
        attendance_db.append({
            'employee_id': emp_id,
            'date': date,
            'status': status
        })
        
    return jsonify({'message': 'Attendance updated'})


# ─── Leaves Routes ────────────────────────────────────────────────────────────

@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    result = []
    for leave in leaves_db:
        emp = next((e for e in employees if e['id'] == int(leave['employee_id'])), None)
        if emp:
            result.append({
                'id': leave['id'],
                'employee_id': emp['id'],
                'first_name': emp['first_name'],
                'last_name': emp['last_name'],
                'department': emp['department'],
                'leave_type': leave['leave_type'],
                'from_date': leave['from_date'],
                'to_date': leave['to_date'],
                'reason': leave['reason'],
                'status': leave['status']
            })
    # Sort so newest are first
    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(result)

@app.route('/api/leaves', methods=['POST'])
def create_leave():
    data = request.get_json()
    new_id = max((l['id'] for l in leaves_db), default=0) + 1
    
    emp_id = int(data.get('employee_id', 0))
    emp = next((e for e in employees if e['id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
        
    new_leave = {
        'id': new_id,
        'employee_id': emp_id,
        'leave_type': data.get('leave_type', ''),
        'from_date': data.get('from_date', ''),
        'to_date': data.get('to_date', ''),
        'reason': data.get('reason', ''),
        'status': 'Pending'
    }
    leaves_db.append(new_leave)
    
    # Return formatted leave for the frontend
    result = {
        'id': new_leave['id'],
        'employee_id': emp['id'],
        'first_name': emp['first_name'],
        'last_name': emp['last_name'],
        'department': emp['department'],
        'leave_type': new_leave['leave_type'],
        'from_date': new_leave['from_date'],
        'to_date': new_leave['to_date'],
        'reason': new_leave['reason'],
        'status': new_leave['status']
    }
    return jsonify(result), 201

@app.route('/api/leaves/<int:leave_id>', methods=['PATCH'])
def update_leave_status(leave_id):
    data = request.get_json()
    status = data.get('status')
    
    leave = next((l for l in leaves_db if l['id'] == leave_id), None)
    if not leave:
        return jsonify({'error': 'Leave not found'}), 404
        
    if status:
        leave['status'] = status
        
    return jsonify({'message': 'Leave updated'})

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
