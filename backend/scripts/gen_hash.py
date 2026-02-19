from passlib.context import CryptContext
pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')
print('admin123 ->', pwd.hash('admin123'))
print('user12345 ->', pwd.hash('user12345'))
