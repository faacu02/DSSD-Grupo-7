from flask import Flask, render_template, request
from controllers.formulario import formulario_bp
from activities.crear_proyecto import bonita_bp
from activities.completar_actividad_siguiente import bonita_bp_siguiente
from classes.request import request_bp

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para los mensajes flash

# Registrar el Blueprint
app.register_blueprint(formulario_bp)
app.register_blueprint(bonita_bp)
app.register_blueprint(bonita_bp_siguiente)
app.register_blueprint(request_bp)

@app.route('/')
def home():
    return '¡Hola, Flask está funcionando!'


if __name__ == '__main__':
    app.run(debug=True)
