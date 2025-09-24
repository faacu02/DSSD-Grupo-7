from flask import Flask, render_template, request, redirect, url_for
from controllers.formulario import formulario_bp
from activities.crear_proyecto import bonita_bp
from classes.request import request_bp

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para los mensajes flash

# Registrar el Blueprint
app.register_blueprint(formulario_bp)
app.register_blueprint(bonita_bp)
app.register_blueprint(request_bp)

@app.route('/')
def home():
    return '¡Hola, Flask está funcionando!'

@app.route('/cargar_etapas', methods=['GET', 'POST'])
def cargar_etapas():
    if request.method == 'POST':
        etapas = []
        for i in range(1, 11):
            nombre = request.form.get(f'etapa_nombre_{i}')
            fecha_i = request.form.get(f'etapa_fecha_inicio_{i}')
            fecha_f = request.form.get(f'etapa_fecha_fin_{i}')
            cobertura = request.form.get(f'etapa_cobertura_{i}')
            if nombre and fecha_i and fecha_f and cobertura:
                etapas.append({
                    'nombre': nombre,
                    'fecha_inicio': fecha_i,
                    'fecha_fin': fecha_f,
                    'cobertura': cobertura
                })
        return f"Etapas cargadas: {etapas}"
    return render_template('formulario_etapas.html')

if __name__ == '__main__':
    app.run(debug=True)
