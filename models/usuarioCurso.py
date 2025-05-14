from models import db

class UsuarioCurso(db.Model):
    __tablename__ = 'usuarios_cursos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),  # ✅ aquí
        nullable=False
    )
    curso_id = db.Column(
        db.Integer, 
        db.ForeignKey('cursos.id', ondelete='CASCADE'),  # ✅ aquí también si quieres
        nullable=False
    )
    fecha_inscripcion = db.Column(db.DateTime)


