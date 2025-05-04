# pip install python-dotenv
# phyton -m pip install pymysql

import pymysql
import os
import dotenv
import time
import hashlib

#cargar las variables de entorno
dotenv.load_dotenv()
#leer las variables de entorno
db_host = os.getenv('db_host')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
print(f"{db_host} {db_name} {db_password} {db_user}")

#Conectar con BD
error = False
error_msg = None
def connectDB():
    try:
        conexion = pymysql.connect(host=db_host,
        user=db_user, passwd=db_password, database=db_name)
        return conexion
    except Exception as e:
        error = True
        error_msg = "Error DB connect"
        print(error_msg)
        return error
    
#Desconectar con BD
def disconnectDB(conexion):
    if conexion:
        conexion.commit()
        conexion.close()

#Comprobar usuario por email
def check_userbymail(email):
    result = None
    conn = connectDB()
    sql = "SELECT * FROM users WHERE email=%s"
    if not error:
        cursor=conn.cursor()
        cursor.execute(sql, email)
        result = cursor.fetchone()
        disconnectDB(conn)
    if result:
        return result
    else:
        return None
    
# print(check_userbymail("pepe@mail.com"))

#método para encriptar password
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()
#print(hash_password("anapass"))

#Crear un método para registrar usuarios
def reg_user(nombre, apellido, email, password):
    result = None
    conn = connectDB()
    cursor=conn.cursor()
    datetime_now = time.strftime("%Y-%m-%d %H:%M:%S")
    hashed_password = hash_password(password)
    sql = "INSERT INTO users (nombre, apellido, email,password, fecha_creacion) VALUES (%s, %s, %s, %s, %s)"
    if not error:
        cursor.execute(sql, (nombre, apellido, email,hashed_password, datetime_now))
        disconnectDB(conn)


def user_addlogin(id: int):
    conn = connectDB()
    cursor=conn.cursor()
    datetime_now = time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO user_sessions (ID_USER, FECHA_LOGIN) VALUES (%s, %s)"
    if not error:
        cursor.execute(sql, (id, datetime_now))
        disconnectDB(conn)


def user_datalogin(id: int):
    conn = connectDB()
    cursor=conn.cursor()
    sql = "SELECT us.fecha_login, u.nombre, u.apellido FROM user_sessions us INNER JOIN users u ON us.id_user=u.id WHERE us.id_user=%s"
    if not error:
        cursor.execute(sql, id)
        results = cursor.fetchall()
        disconnectDB(conn)
    if results:
        results_proc = []
        index = 0
        for item in results:
            index += 1
            result = []
            result.append(index)
            fecha_login = item[0]
            result.append(fecha_login.strftime("%Y-%m-%d %H:%M:%S"))
            result.append(item[1])
            result.append(item[2])
            results_proc.append(result)
        return results_proc
    else:
        return None
    
def get_user_by_id(user_id):
    conn = connectDB()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"Error al obtener usuario por ID: {e}")
        return None
    finally:
        cursor.close()
        disconnectDB(conn)

def update_user_data(user_id, nombre, apellido, nueva_password):
    conn = connectDB()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        hashed = hash_password(nueva_password)
        sql = """UPDATE users 
                 SET nombre = %s, apellido = %s, password = %s 
                 WHERE id = %s"""
        cursor.execute(sql, (nombre, apellido, hashed, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar datos del usuario: {e}")
        return False
    finally:
        cursor.close()
        disconnectDB(conn)

def get_all_users():
    conn = connectDB()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    except Exception as e:
        print("Error al obtener usuarios:", e)
        return []
    finally:
        cursor.close()
        disconnectDB(conn)

def get_users_by_email_filter(email):
    conn = connectDB()
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE email LIKE %s"
        cursor.execute(sql, ('%' + email + '%',))
        return cursor.fetchall()
    except Exception as e:
        print("Error al filtrar usuarios:", e)
        return []
    finally:
        cursor.close()
        disconnectDB(conn)

def toggle_user_status(user_id, new_status):
    conn = connectDB()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET habilitado = %s WHERE id = %s", (new_status, user_id))
        conn.commit()
        return True
    except Exception as e:
        print("Error al cambiar estado del usuario:", e)
        return False
    finally:
        cursor.close()
        disconnectDB(conn)

def get_all_cursos():
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT id, nombre, descripcion, duracion FROM cursos WHERE disponibilidad = TRUE"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursos = []
    columns = [col[0] for col in cursor.description]
    for row in rows:
        cursos.append(dict(zip(columns, row)))
    return cursos


def inscribir_usuario_curso(user_id, curso_id):
    conn = connectDB()
    sql = "INSERT INTO usuarios_cursos (user_id, curso_id) VALUES (%s, %s)"
    cursor = conn.cursor()
    cursor.execute(sql, (user_id, curso_id))
    disconnectDB(conn)

def get_cursos_usuario(user_id):
    conn = connectDB()
    cursor = conn.cursor()
    sql = """
        SELECT c.id, c.nombre, c.descripcion, c.duracion
        FROM cursos c
        JOIN usuarios_cursos uc ON c.id = uc.curso_id
        WHERE uc.user_id = %s
    """
    cursor.execute(sql, (user_id))
    rows = cursor.fetchall()

    cursos = []
    for row in rows:
        cursos.append({
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'duracion': row[3]
        })

    return cursos


def inscribir_usuario(user_id, curso_id):
    conn = connectDB()
    cursor = conn.cursor()

    # Verificar si ya está inscrito
    cursor.execute("SELECT id FROM usuarios_cursos WHERE user_id = %s AND curso_id = %s", (user_id, curso_id))
    if cursor.fetchone():
        return  # Ya está inscrito

    cursor.execute(
        "INSERT INTO usuarios_cursos (user_id, curso_id) VALUES (%s, %s)",
        (user_id, curso_id)
    )
    
    disconnectDB(conn)


def get_cursos_ids_usuario(user_id):
    conn = connectDB()
    cursor = conn.cursor()
    cursor.execute("SELECT curso_id FROM usuarios_cursos WHERE user_id = %s", (user_id,))
    results = cursor.fetchall()
    return {r[0] for r in results}


def get_rol_name_by_id(id_rol):
    conn = connectDB()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usu_rol WHERE id = %s", (id_rol,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_rol_id_by_name(nombre):
    conn = connectDB()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usu_rol WHERE nombre = %s", (nombre,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_user(id_rol, nombre, apellido, email, hashed_pw):
    conn = connectDB()
    cursor = conn.cursor()
    sql = """INSERT INTO users (id_rol, nombre, apellido, email, password, fecha_creacion)
             VALUES (%s, %s, %s, %s, %s, NOW())"""
    cursor.execute(sql, (id_rol, nombre, apellido, email, hashed_pw))
    conn.commit()

def insert_curso(nombre, descripcion, duracion):
    conn = connectDB()
    cursor = conn.cursor()
    sql = """INSERT INTO cursos (nombre, descripcion, duracion, disponibilidad)
             VALUES (%s, %s, %s, TRUE)"""
    cursor.execute(sql, (nombre, descripcion, duracion))
    conn.commit()

def get_cursos_ids_by_usuario(usuario_id):
    conn = connectDB()
    cursor = conn.cursor()
    query = "SELECT curso_id FROM usuarios_cursos WHERE user_id = %s"
    cursor.execute(query, (usuario_id,))
    resultados = cursor.fetchall()
    conn.close()

    # fetchall devuelve lista de tuplas, extraemos los ids:
    return [fila[0] for fila in resultados]

def get_cursos_by_usuario(usuario_id):
    conn = connectDB()
    cursor = conn.cursor()
    
    sql = """
        SELECT c.id, c.nombre, c.descripcion, c.duracion
        FROM cursos c
        JOIN usuarios_cursos uc ON c.id = uc.curso_id
        WHERE uc.user_id = %s
    """
    
    cursor.execute(sql, (usuario_id,))
    cursos = cursor.fetchall()
    conn.close()
    return cursos


# INSTALAR MONGO
# pip install pymongo dnspython