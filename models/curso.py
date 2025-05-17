from models import db

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    duracion = db.Column(db.Integer)
    disponibilidad = db.Column(db.Boolean, default=True, server_default='1')
    imagen_url = db.Column(db.Text)
    slug = db.Column(db.String(100), unique=True)  # Para URLs amigables (ej: "java-principiante")
    mongo_curso_id = db.Column(db.String(50))  # ID referencia a MongoDB (ej: "java_principiante")
