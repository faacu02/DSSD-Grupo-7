from flask import Flask, render_template, request
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

@app.route('/nuevo_proyecto', methods=['GET', 'POST'])
def nuevo_proyecto():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        caracteristicas = request.form['caracteristicas']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
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
        return f"Proyecto creado: {descripcion}, {caracteristicas}, {fecha_inicio} - {fecha_fin}, Etapas: {etapas}"
    return render_template('formulario_proyecto.html')

if __name__ == '__main__':
    app.run(debug=True)
