from flask import Flask, render_template, request, redirect, url_for
from controllers.formulario import formulario_bp
from classes.request import request_bp
from controllers.login import login_bp
from db import db  
from controllers.etapa import etapa_bp
from controllers.donacion import donacion_bp
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para los mensajes flash


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/dssd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Registrar el Blueprint
app.register_blueprint(formulario_bp, url_prefix='')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(request_bp)
app.register_blueprint(etapa_bp, url_prefix='/etapa')
app.register_blueprint(donacion_bp, url_prefix='/donacion')


if __name__ == '__main__':
    app.run(debug=True)


@app.template_filter("to_json")
def to_json_filter(value):
    try:
        return json.loads(value)
    except:
        return value
