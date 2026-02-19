from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.auth import verify_password

s = SessionLocal()
try:
    u = s.query(User).filter(User.username == 'Dani Alonso').first()
    print('User found:', bool(u))
    if u:
        print('stored hash (truncated):', u.password[:60])
        print('verify admin123 ->', verify_password('admin123', u.password))
        print('verify wrong ->', verify_password('nope', u.password))
finally:
    s.close()
