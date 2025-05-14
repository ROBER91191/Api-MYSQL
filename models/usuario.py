from models import db

class Usuario(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('user_rol.id'))
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime)
    fecha_mod = db.Column(db.DateTime)
    tipo=db.Column(db.String(50))
    habilitado = db.Column(db.Boolean, default=True)
