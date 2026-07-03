

# Round 8

### SQL Injection
- Use parameterized queries and ORM filters.
- Never concatenate user input directly into SQL.

```python
name = request.args.get('name')
users = User.query.filter(User.name.ilike(f'%{name}%')).all()
```

### XSS
- Escape output in templates.
- Use `{{ value|e }}` in Jinja2 and avoid injecting raw HTML.

```html
{{ user_input | e }}
```

### CSRF
- Use CSRF tokens for state-changing requests.
- Enable Flask-WTF protection in forms.

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### JWT Tampering
- Always verify signature and expiration.
- Never trust JWT claims without validation.

```python
jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```

### Broken Authentication
- Enforce password hashing and session validation.
- Use secure login checks and logout handling.

```python
from werkzeug.security import generate_password_hash, check_password_hash
hashed = generate_password_hash('password')
check_password_hash(hashed, 'password')
```

### Password Hashing
- Use strong hashing algorithms such as bcrypt or Argon2.
- Never store plain text passwords.

```python
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash('my_password', method='scrypt')
```

### Session Hijacking
- Use secure cookies, HTTPS, and rotate session IDs.
- Regenerate session IDs after login.

```python
session.clear()
session['user_id'] = user.id
```

