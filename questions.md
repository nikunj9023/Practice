
# Coding 1

# creating rest api for user module
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# creating some user
users = [
    {"id": 1, "name": "Nikunj Parmar", "email": "nikunj@example.com"},
    {"id": 2, "name": "Smith", "email": "smith@example.com"}
]

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404
# creating and adding a new user into the database
# creating rest api for user module,company module,employee module,attendancemodule,leave module in python flask


#creating new route
@app.route('/users', methods=['GET'])
def get_users():
    # Logic to retrieve users from the database
    users = [
        {"id": 1, "name": "Nikunj","company":"neevtrust", "role": "Admin","attandence":20,"leave":7},
        {"id": 2, "name": "Pratik","company":"neevtrust", "role": "Editor","attandence":22,"leave":5},
    ]
    return jsonify(users)

#adding data into out database
@app.route('/users', methods=['POST'])
def create_user():
    # Logic to create a new user in the database
    data = request.get_json()
    new_user = {"id": 3, "name": data["name"], "company":data["company"],"role": data["role"],"attandence": data["attandence"]"leave":data["leave"]}
    return jsonify(new_user), 201



# Authentication

#create jwt and refresh token in python using flask and pyjwt
from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

#making a route to generate jwt and refresh token
@app.route('/login', methods=['POST'])
def login():
    auth_data = request.get_json()
    username = auth_data.get('username')
    password = auth_data.get('password')

    # For demonstration, we are using hardcoded username and password
    if username == 'admin' and password == 'password':
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # generate refresh token
        refresh_token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token, 'refresh_token': refresh_token})

    return jsonify({'message': 'Invalid credentials'}), 401

#finally run the flask app
if __name__ == '__main__':
    app.run(debug=True)


# Authorization
#Authorization with Roles like Admin,HR,Manager,Employee in python
#creating login syastem with roles and permissions
login_system = {
    "admin": {"password": "admin123", "role": "Admin"},
    "hr": {"password": "hr123", "role": "HR"},
    "manager": {"password": "manager123", "role": "Manager"},
    "employee": {"password": "employee123", "role": "Employee"},
}
#now creating a function to check the login credentials and return the role of the user
def check_login(username, password):
    user = login_system.get(username)
    if user and user["password"] == password:
        return user["role"]
    else:
        return None
    
#now creating a function to check the permissions of the user based on their role
def check_permissions(role):
    permissions = {
        "Admin": ["create", "read", "update", "delete"],
        "HR": ["read", "update"],
        "Manager": ["read", "update"],
        "Employee": ["read"],
    }
    return permissions.get(role, [])
#now creating a function to simulate the login process
def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    role = check_login(username, password)
    if role:
        print(f"Login successful! Your role is: {role}")
        permissions = check_permissions(role)
        print(f"Your permissions are: {permissions}")
    else:
        print("Invalid username or password.")
#now calling the login function to start the login process
login()


