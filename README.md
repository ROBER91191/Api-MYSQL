# Activar mi (.venv)
source .venv/Scripts/activate

# Instarlar Flask
pip install flask

# Lanzar aplicación
python -m flask run

# Install SQLALCHEMY (ORM)
pip install flask-sqlalchemy flask-migrate python-dotenv

# Evitar problema con la aplicación FLASK_APP
set FLASK_APP=app.py 
