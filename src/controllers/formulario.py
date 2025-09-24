from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests

# Crear el Blueprint
formulario_bp = Blueprint('formulario', __name__)

@formulario_bp.route('/formulario_nombre', methods=['GET', 'POST'])
def formulario_nombre():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if nombre:
            try:
                response = requests.post(
                    url_for('bonita.completar_actividad', _external=True),
                    json={"nombre": nombre}
                )
                data = response.json()
                if data.get("success"):
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}', 'success')
                else:
                    flash(f'Error al crear proyecto: {data.get('error')}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            return redirect(url_for('cargar_etapas'))
        else:
            flash('Por favor, ingresa un nombre válido.', 'error')
    return render_template('formulario_nombre.html')