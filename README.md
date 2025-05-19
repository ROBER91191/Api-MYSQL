# Guía de Instalación y Configuración

## Entorno Virtual

```bash
# Activar entorno virtual (.venv)
source .venv/Scripts/activate
```

## Instalación de Dependencias

```bash
# Instalar Flask
pip install flask

# Instalar SQLAlchemy (ORM)
pip install flask-sqlalchemy flask-migrate python-dotenv

# Instalar MongoDB
pip install pymongo
pip install python-slugify
```

## Configuración de la Aplicación

```bash
# Configurar variable de entorno para Flask
set FLASK_APP=app.py

# Lanzar aplicación
python -m flask run
```

## Migraciones de Base de Datos

```bash
# Inicializar migraciones
flask db init

# Crear migración
flask db migrate -m "Initial migration"

# Aplicar migración
flask db upgrade
```

## MongoDB

El proyecto incluye un archivo `mongo.db` con la estructura de datos para los cursos. Los datos incluyen cursos de Java, SQL, Python, React y Node.js, con sus respectivas secciones y temas.

### Comandos útiles para MongoDB

```bash
# Iniciar el cliente de MongoDB
mongo

# Listar bases de datos
show dbs

# Usar una base de datos específica
use nombredb

# Listar colecciones
show collections

# Insertar un documento
db.cursos.insertOne({
  "curso_id": "ejemplo_curso",
  "nombre": "Nombre del Curso",
  "descripcion": "Descripción del curso"
})

# Consultar todos los documentos de una colección
db.cursos.find()

# Consultar documentos con filtro
db.cursos.find({"nivel": "principiante"})

# Importar datos desde un archivo JSON
mongoimport --db nombredb --collection cursos --file ruta/archivo.json --jsonArray
```

### Estructura de Datos

Los datos de cursos están estructurados de la siguiente manera:
- Cursos (con ID, nombre, descripción, duración y nivel)
- Secciones dentro de cada curso
- Temas dentro de cada sección

## Docker

Utiliza el siguiente archivo `docker-compose.yml` para crear un servidor MySQL:

```yaml
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: Password95
    MYSQL_DATABASE: mydb
    MYSQL_USER: rserpa
    MYSQL_PASSWORD: rserpa95
  ports:
    - "3306:3306"
```

También puedes añadir MongoDB a tu configuración de Docker:

```yaml
mongodb:
  image: mongo:latest
  ports:
    - "27017:27017"
  volumes:
    - ./mongo-data:/data/db
```
