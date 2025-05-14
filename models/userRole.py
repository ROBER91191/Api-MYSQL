from models import db

class UserRole(db.Model):
    __tablename__ = 'user_rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True)