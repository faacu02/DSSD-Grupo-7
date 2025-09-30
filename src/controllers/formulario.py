from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
import services.proyecto_servicce as proyecto_service
# Crear el Blueprint
formulario_bp = Blueprint('formulario', __name__)

@formulario_bp.route('/formulario_nombre', methods=['GET', 'POST'])
def formulario_nombre():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cantidad_etapas = request.form.get('cantidad_etapas')
        if nombre and cantidad_etapas:
            try:
                proyecto_service.crear_proyecto(nombre, cantidad_etapas)
                response = requests.post(
                    url_for('bonita.completar_actividad', _external=True),
                    json={"nombre": nombre, "cantidad_etapas": cantidad_etapas}
                )
                data = response.json()
                if data.get("success"):
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}, Etapas: {cantidad_etapas}', 'success')
                else:
                    flash(f'Error al crear proyecto: {data.get("error")}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            return redirect(url_for('formulario.formulario_nombre'))
        else:
            flash('Por favor, ingresa un nombre y cantidad de etapas válidos.', 'error')
    return render_template('formulario_nombre.html')