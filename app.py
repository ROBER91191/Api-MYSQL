from flask import Flask, render_template, request,make_response, redirect, url_for
import db, validate

app=Flask(__name__)

# source .venv/Scripts/activate
# pip install flask
# python -m flask run

@app.route('/')
def home():
    return render_template('home.html')

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
                    db.user_addlogin(int(new_user[0]))
                    #redirigir a destino y logar
                    # id_user = new_user[0]
                    # nombre = new_user[3][:1]
                    # apellido = new_user[4][:1]
                    cookie_str = str(new_user[0]) + "_" + new_user[3][:1] +new_user[4][:1]
                    resp = make_response(redirect(url_for('userdata',
                    id=new_user[0])))
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

        cursos = db.get_all_cursos()

        if results:
            return render_template("userdata.html", show_data_aftersend =
            True, rerror=False, results=results, total=total,cursos=cursos)
        else:
            return render_template("userdata.html", show_data_aftersend =
            True, rerror = False, rerror_msg = "En este momento no podemos procesar la solicitud, inténtalo de nuevo más tarde", cursos=[])
    else:
        return render_template("userdata.html", show_data_aftersend =
        True, rerror=False, rerror_msg="Debes estar logado para ver esta sección",cursos=[])


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
                if db.hash_password(val_passw) == loged_user[6]:
                    # OK
                    db.user_addlogin(int(loged_user[0]))

                    # Función auxiliar para evitar error con None
                    def safe_initial(value):
                        return value[:1] if value else "_" # si el campo es None o vacío, devuelve "_"
                    
                    # Creamos la cookie con el ID del usuario y las iniciales del nombre y apellido
                    # Ejemplo: "14_RS" si el usuario tiene ID 14, nombre "Roberto", apellido "Serpa"
                    cookie_str = f"{loged_user[0]}_{safe_initial(loged_user[3])}{safe_initial(loged_user[4])}"

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
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie("usu")
    return resp

# Añado variable is_logged_in a todas las plantillas de forma automática
@app.context_processor
def inject_user_cookie():
    valor_usucookie = request.cookies.get('usu')
    return dict(is_logged_in=valor_usucookie is not None)

@app.route("/cursos")
def mostrar_cursos():
    cursos = db.get_all_cursos()
    return render_template("cursos.html", cursos=cursos)

@app.route("/cursos/<int:id>/inscribir", methods=["POST"])
def inscribirse_curso(id):
    cookie_str = request.cookies.get("usu")
    if not cookie_str:
        return redirect(url_for("login"))
    
    user_id = int(cookie_str.split("_")[0])
    db.inscribir_usuario_curso(user_id, id)
    return redirect(url_for("mis_cursos"))


@app.route("/mis-cursos")
def mis_cursos():
    cookie_str = request.cookies.get("usu")
    if not cookie_str:
        return redirect(url_for("login"))
    
    user_id = int(cookie_str.split("_")[0])
    cursos = db.get_cursos_usuario(user_id)
    return render_template("mis_cursos.html", cursos=cursos)
