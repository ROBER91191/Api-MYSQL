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
print(check_userbymail("pepe@mail.com"))

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
    cursor = connectDB()
    sql = """SELECT US. FECHA_LOGIN, U.NOMBRE, U.APELLIDO
    FROM pruebaiwii.user_sessions US
    INNER JOIN pruebaiwii.users U ON US.ID_USER=U.ID
    WHERE US.ID_USER=%s"""
    if not error:
        cursor.execute(sql, id)
        results = cursor.fetchall()
        disconnectDB()
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
    
# reg_user("Ana", "Larra", "ana2@mail.com", "anapass")

# # Conectar con base de datos
# conexion = pymysql.connect(host=db_host,
# user=db_user,
# passwd=db_password,
# database=db_name)
# cursor = conexion.cursor()

# sql = "SELECT * FROM Usuarios"
# # Mostrar registros
# cursor.execute(sql)
# filas = cursor.fetchall()
# for fila in filas:
#     print(fila)
# # Finalizar
# conexion.commit()
# conexion.close()