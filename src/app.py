from flask import Flask, render_template, request, redirect, url_for
from controllers.formulario import formulario_bp
from activities.crear_proyecto import bonita_bp
from activities.completar_actividad_siguiente import bonita_bp_siguiente
from classes.request import request_bp
from db import db  # <--- Importa db desde db.py

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para los mensajes flash


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/dssd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Registrar el Blueprint
app.register_blueprint(formulario_bp, url_prefix='')
app.register_blueprint(bonita_bp)
app.register_blueprint(bonita_bp_siguiente)
app.register_blueprint(request_bp)


if __name__ == '__main__':
    app.run(debug=True)
