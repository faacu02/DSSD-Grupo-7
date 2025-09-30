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
                    # Obtener el case_id del resultado
                    case_id = data["result"].get("caseId") if data.get("result") else None
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}', 'success')
                    if case_id:
                        # Redirigir a cargar_etapa y pasar el case_id por la URL
                        return redirect(url_for('formulario.cargar_etapa', case_id=case_id))
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}, Etapas: {cantidad_etapas}', 'success')
                else:
                    flash(f'Error al crear proyecto: {data.get("error")}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            return redirect(url_for('formulario.formulario_nombre'))
        else:
            flash('Por favor, ingresa un nombre válido.', 'error')
    # Obtener case_id de la URL si existe y pasarlo al template
    case_id = request.args.get('case_id')
    return render_template('formulario_nombre.html', case_id=case_id)

@formulario_bp.route('/cargar_etapa', methods=['GET', 'POST'])
def cargar_etapa():
    if request.method == 'POST':
        case_id = request.form.get('case_id')
        nombre_etapa = request.form.get('nombre_etapa')
        if case_id and nombre_etapa:
            try:
                response = requests.post(
                    url_for('bonita_siguiente.completar_actividad_siguiente', _external=True),
                    json={"case_id": case_id, "nombre": nombre_etapa}
                )
                data = response.json()
                if data.get("success"):
                    flash(f'Etapa cargada correctamente para el caso {case_id}', 'success')
                else:
                    flash(f'Error al cargar etapa: {data.get("error")}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            return redirect(url_for('formulario.cargar_etapa', case_id=case_id))
        else:
            flash('Por favor, completa todos los campos.', 'error')
    # Obtener case_id de la URL si existe y pasarlo al template
    case_id = request.args.get('case_id')
    return render_template('cargar_etapa.html', case_id=case_id)
