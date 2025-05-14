from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from models import db as orm_db
import db  # tu lógica de negocio / servicios
import os
from dotenv import load_dotenv
import validate  # tu módulo de validaciones
import uuid
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_por_defecto')  # ✅ asegúrate de tener esto en tu .env

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://usuario:clave@localhost/mydb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar ORM
orm_db.init_app(app)


# source .venv/Scripts/activate
# pip install flask
# python -m flask run

@app.route("/")
def home():
    return render_template("home.html", active_page="home")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", show_data_aftersend= False, rerror = False)

    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        passw = request.form.get("passw")
        #print(f"{nombre} {apellido} {email} {passw}")
        #comprobamos los datos - la comprobación puede ser tanexahustiva como requiera
        val_nombre = validate.check_str(nombre)
        val_apellido = validate.check_str(apellido)
        val_email = validate.check_mail(email)
        val_passw = validate.check_passw(passw)
        if val_nombre and val_apellido and val_email and val_passw:
        #ver si ya está registrado el email
            if db.check_userbymail(val_email):
                #usu registrado previamente
                return render_template("signup.html",
                show_data_aftersend = True, rerror = True, rerror_msg = "Ya existe un registro para este usuario", nombre = nombre, apellido =
                apellido, email = email, passw = passw)
            else:
                #insertar registro
                db.reg_user(val_nombre,val_apellido,val_email, val_passw)
                #comprobamos que se ha insertado correctamente
                new_user = db.check_userbymail(val_email)

                if new_user:
                    db.user_addlogin(int(new_user.id))
                    #redirigir a destino y logar
                    # id_user = new_user[0]
                    # nombre = new_user[3][:1]
                    # apellido = new_user[4][:1]
                    cookie_str = str(new_user.id) + "_" + new_user.nombre +new_user.apellido
                    resp = make_response(redirect(url_for('userdata',
                    id=new_user.id)))
                    resp.set_cookie("usu", cookie_str, max_age=60*5)
                    #60*60*24
                    return resp
                #logar y redirigir a destino
                else:
                    return render_template("signup.html",
                    show_data_aftersend = True, rerror = True, rerror_msg = "En este momento no podemos procesar la solicitud, inténtalo de nuevo más tarde", 
                    nombre = nombre, apellido = apellido, email = email, passw = passw)
                
        else:
            return render_template("signup.html",
            show_data_aftersend = True, rerror = True, rerror_msg = "Error en los datos, no se puede completar el registro", nombre = nombre,
            apellido = apellido, email = email, passw = passw)
        

@app.route("/userdata/<id>")
def userdata(id):
    cookies = request.cookies
    #print(cookies)
    valor_usucookie = cookies.get('usu')
    cookid = 0

    if valor_usucookie != None:
        # Encontrar la posición del guion bajo
        cookid_index = valor_usucookie.index('_')

        # EXTRAER el ID desde el principio hasta el "_"
        cookid_str  = valor_usucookie[:cookid_index] # ← aquí estaba el error: antes usabas el índice como si fuera string

        cookid = int(cookid_str)  # convertir a entero

    if int(id) == int(cookid):
        #mostrar datos
        results = db.user_datalogin(id)
        total = len(results)

        cursos = db.get_cursos_usuario(cookid)

        if results:
            return render_template("mis_cursos.html", show_data_aftersend =
            True, rerror=False, results=results, total=total,cursos=cursos)
        else:
            return render_template("mis_cursos.html", show_data_aftersend =
            True, rerror = False, rerror_msg = "En este momento no podemos procesar la solicitud, inténtalo de nuevo más tarde", cursos=[])
    else:
        return render_template("mis_cursos.html", show_data_aftersend =
        True, rerror=False, rerror_msg="Debes estar logado para ver esta sección", cursos=[])


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", show_data_aftersend=False, rerror=False)

    if request.method == "POST":
        email = request.form.get("email")
        passw = request.form.get("passw")
        val_email = validate.check_mail(email)
        val_passw = validate.check_passw(passw)

        if val_email and val_passw:
            # comprobar que está registrado el email
            if db.check_userbymail(val_email):
                ###adding code
                loged_user = db.check_userbymail(val_email)
                # comprobar coincidencia de passw
                if db.hash_password(val_passw) == loged_user.password:
                    # OK
                    db.user_addlogin(int(loged_user.id))

                    # Recuperar ID del rol (suponemos que está en loged_user[1])
                    session['role'] = db.get_rol_name_by_id(loged_user.id_rol)

                    # Función auxiliar para evitar error con None
                    def safe_initial(value):
                        return value[:1] if value else "_" # si el campo es None o vacío, devuelve "_"
                    
                    # Creamos la cookie con el ID del usuario y las iniciales del nombre y apellido
                    # Ejemplo: "14_RS" si el usuario tiene ID 14, nombre "Roberto", apellido "Serpa"
                    cookie_str = f"{loged_user.id}_{safe_initial(loged_user.nombre)}{safe_initial(loged_user.apellido)}"

                    # Creamos una respuesta con redirección a la vista userdata con el ID
                    resp = make_response(redirect(url_for('mostrar_cursos')))

                    # Guardamos la cookie "usu", válida por 5 minutos (300 segundos)
                    resp.set_cookie("usu", cookie_str, max_age=60*5)
                    return resp
                else:
                    return render_template("login.html", show_data_aftersend=True, rerror=True,
                                        rerror_msg="No se ha podido completar el login con estos datos",
                                        email=email, passw=passw)
            else:
                return render_template("login.html", show_data_aftersend=True, rerror=True,
                                    rerror_msg="No se ha podido completar el login con estos datos",
                                    email=email, passw=passw)
        else:
            return render_template("login.html", show_data_aftersend=True, rerror=True,
                                rerror_msg="Error en los datos, no se puede completar el registro",
                                email=email, passw=passw)


@app.route("/userdata/edit", methods=["GET", "POST"])
def edit_user():
    cookie = request.cookies.get("usu")
    if not cookie:
        return redirect(url_for("login"))
    
    try:
        user_id = int(cookie.split("_")[0])
    except:
        return redirect(url_for("login"))

    user = db.get_user_by_id(user_id)
    if not user:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("edit_user.html", user=user, updated=False, error=False)

    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        nueva_pass = request.form.get("passw")

        # Validaciones básicas (puedes usar validate si lo prefieres)
        if not nombre or not apellido or not nueva_pass:
            return render_template("edit_user.html", user=user, updated=False, error=True, error_msg="Todos los campos son obligatorios.")

        result = db.update_user_data(user_id, nombre, apellido, nueva_pass)
        user = db.get_user_by_id(user_id)  # refrescar datos por si cambió algo

        if result:
            return render_template("edit_user.html", user=user, updated=True, error=False)
        else:
            return render_template("edit_user.html", user=user, updated=False, error=True, error_msg="Error al actualizar los datos.")


@app.route("/userdata/all")
def all_users():
    cookie = request.cookies.get("usu")
    if not cookie:
        return redirect(url_for("login"))

    try:
        user_id = int(cookie.split("_")[0])
    except:
        return redirect(url_for("login"))

    current_user = db.get_user_by_id(user_id)
    if not current_user:
        return redirect(url_for("login"))

    user_rol_id = current_user[6]  # id_rol está en índice 6
    if user_rol_id not in [1, 2]:  # solo super(1) y admin(2)
        return redirect(url_for("home"))

    filtro_email = request.args.get("email")
    if filtro_email:
        users = db.get_users_by_email_filter(filtro_email)
    else:
        users = db.get_all_users()

    return render_template("all_users.html", users=users, current_user=current_user)


@app.route("/userdata/toggle/<int:id>/<int:new_status>")
def toggle_user(id, new_status):
    cookie = request.cookies.get("usu")
    if not cookie:
        return redirect(url_for("login"))
    try:
        user_id = int(cookie.split("_")[0])
    except:
        return redirect(url_for("login"))
    current_user = db.get_user_by_id(user_id)
    if not current_user or current_user[6] != 1:  # solo super
        return redirect(url_for("home"))
    db.toggle_user_status(id, new_status)
    return redirect(url_for("all_users"))


@app.route("/logout")
def logout():
    # Elimina cualquier dato de sesión o cookie
    session.clear()

    # Elimina cookie personalizada si la estás usando
    resp = make_response(render_template("home.html"))
    resp.set_cookie("usu", "", expires=0)

    return resp


# Añado variable is_logged_in a todas las plantillas de forma automática
@app.context_processor
def inject_user_cookie():
    valor_usucookie = request.cookies.get('usu')
    return dict(is_logged_in=valor_usucookie is not None)


@app.route("/cursos")
def mostrar_cursos():
    usuario_id = db.get_usuario_id_desde_cookie()
    cursos = db.get_all_cursos()
    cursos_inscritos = db.get_cursos_ids_by_usuario(usuario_id)
    return render_template("cursos.html", cursos=cursos, cursos_inscritos=cursos_inscritos)


@app.route("/inscribirse/<int:curso_id>", methods=["POST"])
def inscribirse(curso_id):
    cookie = request.cookies.get("usu")

    if not cookie:
        return redirect(url_for("login"))

    user_id = int(cookie.split("_")[0])

    db.inscribir_usuario_curso(user_id, curso_id)  # esta función hay que definirla abajo 👇

    return redirect(url_for("mostrar_cursos", mensaje="inscrito"))


@app.route("/mis_cursos")
def mis_cursos():
    usuario_id = db.get_usuario_id_desde_cookie()
    cursos = db.get_cursos_by_usuario(usuario_id)
    return render_template("mis_cursos.html", cursos=cursos, active_page="mis_cursos")


@app.route("/admin", methods=["GET"])
def admin():
    if session.get("role") not in ["admin","super"]:
        flash("Acceso denegado", "danger")
        return redirect(url_for("mostrar_cursos"))

    usuarios = db.get_all_usuarios_with_roles()
    cursos = db.get_all_cursos()
    return render_template("admin.html", usuarios=usuarios, cursos=cursos, active_page="admin")



@app.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    if session.get("role") not in ["admin", "super"]:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("mostrar_cursos"))

    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    email = request.form.get("email")
    password = request.form.get("passw")
    role = request.form.get("role")

    # 👇 Mapea role a ID en tu tabla roles
    role_map = {"user": 3, "admin": 2, "super": 1}
    id_rol = role_map.get(role)

    if not id_rol:
        flash("Rol inválido.", "warning")
        return redirect(url_for("admin"))

    if db.check_userbymail(email):
        flash("Ya existe un usuario con ese correo.", "warning")
        return redirect(url_for("admin"))

    hashed = db.hash_password(password)
    db.insert_user(nombre, apellido, email, hashed, id_rol)
    flash("Usuario creado con éxito ✅", "success")
    return redirect(url_for("admin"))


@app.route("/agregar_curso", methods=["POST"])
def agregar_curso():
    if session.get("role") not in ["admin", "super"]:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("mostrar_cursos"))

    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    duracion = request.form.get("duracion")
    imagen = request.files.get("imagen")

    imagen_url = None
    if imagen and imagen.filename != '':
        # filename = secure_filename(f"{uuid.uuid4().hex}_{imagen.filename}")
        filename = secure_filename(f"{imagen.filename}")
        ruta = os.path.join("static/uploads", filename)
        imagen.save(ruta)
        imagen_url = f"/static/uploads/{filename}"

    db.insert_curso(nombre, descripcion, duracion,imagen_url)
    flash("Curso agregado con éxito ✅", "success")
    return redirect(url_for("admin"))


@app.route("/abandonar_curso/<int:curso_id>", methods=["POST"])
def abandonar_curso(curso_id):
    usuario_id = db.get_usuario_id_desde_cookie()
    if not usuario_id:
        return redirect(url_for("login"))

    db.eliminar_usuario_curso(usuario_id, curso_id)
    flash("Te has dado de baja del curso.", "info")
    return redirect(url_for("mis_cursos"))


@app.route("/borrar_usuario/<int:usuario_id>", methods=["POST"])
def borrar_usuario(usuario_id):
    if session.get("role") not in ["admin", "super"]:
        flash("No autorizado", "danger")
        return redirect(url_for("admin"))

    db.delete_usuario(usuario_id)
    flash("Usuario eliminado", "success")
    return redirect(url_for("admin"))


@app.route("/borrar_curso/<int:curso_id>", methods=["POST"])
def borrar_curso(curso_id):
    if session.get("role") not in ["admin", "super"]:
        flash("No autorizado", "danger")
        return redirect(url_for("admin"))

    db.delete_curso(curso_id)
    flash("Curso eliminado", "success")
    return redirect(url_for("admin"))

