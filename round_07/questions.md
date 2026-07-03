
# Round 7

## Candidate gets A broken Flask Project

### Problem
A candidate is given a Flask project with these issues:
- Authentication not working
- Pagination bug
- SQL Injection
- N+1 Query
- Memory Leak
- Circular Import
- Wrong Migration
- Missing Index

They must fix all of them.

### Solution

#### 1. Authentication not working
- Use a proper login flow with hashed passwords.
- Use JWT or Flask-Login with a decorator.
- Always validate token before protected routes.

```python
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

users = {
    'admin': generate_password_hash('password')
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and check_password_hash(users[username], password):
        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401
```

#### 2. Pagination bug
- Use SQLAlchemy pagination correctly.
- Always pass `page` and `per_page` safely.

```python
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)

result = User.query.order_by(User.id).paginate(page=page, per_page=per_page, error_out=False)
```

#### 3. SQL Injection
- Never build SQL strings with user input.
- Use ORM filters or parameterized queries.

```python
name = request.args.get('name')
users = User.query.filter(User.name.ilike(f'%{name}%')).all()
```

#### 4. N+1 Query
- Use `joinedload` or `selectinload` for relationships.

```python
from sqlalchemy.orm import joinedload

orders = Order.query.options(joinedload(Order.customer)).all()
```

#### 5. Memory Leak
- Close database sessions properly.
- Avoid storing large objects in global memory.
- Clear caches and remove unused references.

```python
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
db = SQLAlchemy(app)
```

#### 6. Circular Import
- Use an application factory pattern.
- Keep models and routes in separate modules.

```python
# app/__init__.py
from flask import Flask
from .routes import main
from .models import db


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    db.init_app(app)
    return app
```

#### 7. Wrong Migration
- Always generate migrations after model changes.
- Check Alembic revision history before applying.

```bash
flask db migrate -m "add user table"
flask db upgrade
```

#### 8. Missing Index
- Add indexes on frequently filtered and joined columns.

```python
from sqlalchemy import Index

Index('idx_user_email', User.email)
```