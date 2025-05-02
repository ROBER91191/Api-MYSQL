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
                    cookie_str = str(new_user[0]) + "_" + new_user[1][:1] +new_user[2][:1]
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
        if results:
            return render_template("userdata.html", show_data_aftersend =
            True, rerror=False, results=results, total=total)
        else:
            return render_template("userdata.html", show_data_aftersend =
            True, rerror = False, rerror_msg = "En este momento no podemos procesar la solicitud, inténtalo de nuevo más tarde")
    else:
        return render_template("userdata.html", show_data_aftersend =
        True, rerror=False, rerror_msg="Debes estar logado para ver esta sección")


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
                    resp = make_response(redirect(url_for('userdata',
                                                        id=loged_user[0])))
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


#ejecutar el archivo principal
if __name__ == '__main__':
    app.run()
