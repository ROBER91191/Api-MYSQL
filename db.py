from models import db
from models.usuario import Usuario
from models.curso import Curso
from models.usuarioCurso import UsuarioCurso
from models.userSessions import UserSession
from models.userRole import UserRole
from sqlalchemy.exc import IntegrityError
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
from datetime import datetime
import hashlib
import pymongo
import sys
from flask import abort
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from slugify import slugify  # pip install python-slugify

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['MongoDb']

uri = 'localhost:27017'
# Conexión optimizada
try:
    # Versión con manejo de errores
    mongo_client = MongoClient('mongodb://localhost:27017/', 
                             serverSelectionTimeoutMS=5000)  # Timeout de 5 segundos
    mongo_client.server_info()  # Forza una prueba de conexión
    mongo_db = mongo_client['MongoDb']  # Nombre de tu base de datos
    print("✅ Conexión a MongoDB exitosa")
except ConnectionFailure as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)

# ========================
# FUNCIONES UTILITARIAS
# ========================

def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


# ========================
# USERS
# ========================

def check_userbymail(email):
    return Usuario.query.filter_by(email=email).first()

def insert_user(nombre, apellido, email, password, id_rol=3):
    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        password=password,
        id_rol=id_rol,
        fecha_creacion=datetime.now(),
        habilitado=True
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

def get_user_by_id(id):
    return Usuario.query.get(id)

def update_user_data(id, nombre, apellido, nueva_pass):
    usuario = Usuario.query.get(id)
    if not usuario:
        return False
    usuario.nombre = nombre
    usuario.apellido = apellido
    usuario.password = hash_password(nueva_pass)
    usuario.fecha_modificacion = datetime.now()
    db.session.commit()
    return True

def get_all_users():
    return Usuario.query.all()

def get_users_by_email_filter(email):
    return Usuario.query.filter(Usuario.email.like(f"%{email}%")).all()

def toggle_user_status(user_id, habilitado):
    user = Usuario.query.get(user_id)
    if not user:
        return False
    
    user.habilitado = habilitado
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar curso {user}: {e}")
        return False

def get_usuario_id_desde_cookie():
    from flask import request
    usu_cookie = request.cookies.get("usu")
    if usu_cookie:
        try:
            # Se espera un formato tipo "14_RS" → ID_nombreInicialApellidoInicial
            usuario_id = int(usu_cookie.split("_")[0])
            return usuario_id
        except (IndexError, ValueError):
            return None
    return None



def get_usuario_by_id(user_id):
    return Usuario.query.get(user_id)


def update_usuario_con_imagen(user, nombre, apellido, nueva_pass=None, imagen=None):
    user.nombre = nombre
    user.apellido = apellido

    if nueva_pass:
        user.password = hash_password(nueva_pass)

    if imagen and imagen.filename != "":
        filename = secure_filename(f"{uuid.uuid4().hex}_{imagen.filename}")
        ruta = os.path.join("static/uploads", filename)
        imagen.save(ruta)
        user.imagen_url = f"/static/uploads/{filename}"
    
    db.session.commit()
    return user

def actualizar_usuario_por_admin(user, nombre, apellido, email, rol_nombre, nueva_pass=None, imagen=None):
    user.nombre = nombre
    user.apellido = apellido
    user.email = email
    user.id_rol = get_rol_id_by_name(rol_nombre)

    if nueva_pass:
        from db import hash_password
        user.password = hash_password(nueva_pass)

    if imagen and imagen.filename != "":
        filename = secure_filename(f"{uuid.uuid4().hex}_{imagen.filename}")
        ruta = os.path.join("static/uploads", filename)
        imagen.save(ruta)
        user.imagen_url = f"/static/uploads/{filename}"

    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


def delete_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

def get_all_usuarios_with_roles():
    roles = {r.id: r.nombre for r in UserRole.query.all()}
    current_user_id = get_usuario_id_desde_cookie()
    usuarios = Usuario.query.filter(Usuario.id != current_user_id).all()
    for u in usuarios:
        u.rol_nombre = roles.get(u.id_rol, "Desconocido")
    return usuarios

# ========================
# CURSOS
# ========================

def get_all_cursos():
    return Curso.query.all()

def get_availables_cursos():
    return Curso.query.filter_by(disponibilidad=1).all()

def insert_curso(nombre, descripcion, duracion, imagen_url):
    # Paso 1: Buscar en MongoDB por nombre para encontrar curso_id existente
    doc_existente = mongo_db.cursos.find_one({"nombre": nombre})
    
    if doc_existente:
        # Usar el curso_id existente
        mongo_curso_id = doc_existente["curso_id"]
    else:
        # Crear nuevo ID si no existe (usando slug para nombres nuevos)
        mongo_curso_id = slugify(nombre, separator="_")
        mongo_db.cursos.insert_one({
            "curso_id": mongo_curso_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "duracion_total_horas": duracion,
            "secciones": []
        })

    # Paso 2: Generar slug único para SQL
    slug = generar_slug_unico(nombre)  # Usar la función que maneja duplicados

    # Paso 3: Crear curso en SQL
    nuevo_curso = Curso(
        nombre=nombre,
        descripcion=descripcion,
        duracion=duracion,
        imagen_url=imagen_url,
        mongo_curso_id=mongo_curso_id,
        slug=slug
    )

    db.session.add(nuevo_curso)
    db.session.commit()
    return nuevo_curso

def generar_slug_unico(nombre):
    base_slug = slugify(nombre)
    contador = 1
    nuevo_slug = base_slug

    while Curso.query.filter_by(slug=nuevo_slug).first() is not None:
        nuevo_slug = f"{base_slug}-{contador}"
        contador += 1

    return nuevo_slug

def get_curso_by_id(curso_id):
    return Curso.query.get(curso_id)

def get_contenido_mongo_por_curso_id(mongo_id):
    return mongo_db.cursos.find_one({"curso_id": mongo_id})

def get_cursos_by_usuario(user_id):
    return Curso.query.join(UsuarioCurso).filter(UsuarioCurso.user_id == user_id).all()

def get_cursos_ids_by_usuario(user_id):
    return [uc.curso_id for uc in UsuarioCurso.query.filter_by(user_id=user_id).all()]

def get_cursos_usuario(user_id):
    cursos = (
        db.session.query(Curso)
        .join(UsuarioCurso, Curso.id == UsuarioCurso.curso_id)
        .filter(UsuarioCurso.user_id == user_id)
        .all()
    )
    return cursos

def actualizar_curso(curso, nombre, descripcion, duracion, imagen=None, disponible=None):

    curso.nombre = nombre
    curso.descripcion = descripcion
    curso.duracion = duracion
    
    if disponible is not None:
        curso.disponible = disponible
    
    if imagen and imagen.filename != '':
        # Eliminar imagen anterior si existe
        if curso.imagen_url:
            try:
                os.remove(os.path.join('static', curso.imagen_url.lstrip('/')))
            except OSError:
                pass  # Si no existe el archivo, continuamos
        
        # Guardar nueva imagen
        filename = secure_filename(f"{uuid.uuid4().hex}_{imagen.filename}")
        upload_path = os.path.join('static', 'uploads', 'cursos', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        imagen.save(upload_path)
        curso.imagen_url = f"/static/uploads/cursos/{filename}"

    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar curso: {str(e)}")
        return False
    
def delete_curso(curso_id):
    curso = Curso.query.get(curso_id)
    if curso:
        db.session.delete(curso)
        db.session.commit()

# Para cambiar disponibilidad
def toggle_curso_status(curso_id, disponible):
    curso = Curso.query.get(curso_id)
    if not curso:
        return False
    
    curso.disponibilidad = disponible
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar curso {curso_id}: {e}")
        return False


def get_curso_content(curso_slug):
    # 1. Obtener el curso de SQL para sacar la referencia a MongoDB
    curso = Curso.query.filter_by(slug=curso_slug).first()
    if not curso:
        abort(404)
    
    # 2. Obtener contenido de MongoDB
    contenido = mongo_db.cursos.find_one({"curso_id": curso.slug})
    if not contenido:
        abort(404)
    
    return {
        "curso": curso,
        "contenido": contenido
    }

# ========================
# INSCRIPCIONES
# ========================
def reg_user(nombre_user, apellido_user, email_user, password_user):
    existe = Usuario.query.filter_by(email=email_user).first()
    if existe:
        return
    inscripcion = Usuario(
    nombre=nombre_user,
    apellido=apellido_user,
    email=email_user,
    password=hash_password(password_user),
    fecha_creacion=datetime.now(),
    habilitado=True,
    id_rol=3 
    )
    db.session.add(inscripcion)
    db.session.commit()

def inscribir_usuario(user_id, curso_id):
    existe = UsuarioCurso.query.filter_by(id_usuario=user_id, id_curso=curso_id).first()
    if existe:
        return
    inscripcion = UsuarioCurso(id_usuario=user_id, id_curso=curso_id)
    db.session.add(inscripcion)
    db.session.commit()


def inscribir_usuario_curso(user_id, curso_id):
    try:
        inscripcion = UsuarioCurso(user_id=user_id, curso_id=curso_id)
        db.session.add(inscripcion)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False  # Ya estaba inscrito u otro problema
    except Exception as e:
        db.session.rollback()
        print(f"Error inscribiendo al usuario: {e}")
        return False

def eliminar_usuario_curso(usuario_id, curso_id):
    inscripcion = UsuarioCurso.query.filter_by(user_id=usuario_id, curso_id=curso_id).first()
    if inscripcion:
        db.session.delete(inscripcion)
        db.session.commit()

# ========================
# LOGIN SESSIONS
# ========================

def user_addlogin(user_id):
    login = UserSession(id_user=user_id, fecha_login=datetime.now())
    db.session.add(login)
    db.session.commit()

def user_datalogin(user_id):
    return UserSession.query.filter_by(id_user=user_id).all()

# ========================
# ROLES
# ========================

def get_rol_name_by_id(id_rol):
    rol = UserRole.query.get(id_rol)
    return rol.nombre if rol else None

def get_rol_id_by_name(nombre):
    rol = UserRole.query.filter_by(nombre=nombre).first()
    return rol.id if rol else None


