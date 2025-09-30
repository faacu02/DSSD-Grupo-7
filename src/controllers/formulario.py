from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
import services.proyecto_servicce as proyecto_service
import services.etapa_service as etapa_service
from datetime import datetime

# Crear el Blueprint
formulario_bp = Blueprint('formulario', __name__)


def to_timestamp(fecha_str):
    if not fecha_str:
        return None
    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

@formulario_bp.route('/formulario_nombre', methods=['GET', 'POST'])
def formulario_nombre():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if nombre:
            try:
                proyecto = proyecto_service.crear_proyecto(nombre)
                response = requests.post(
                    url_for('bonita.completar_actividad', _external=True),
                    json={"nombre": nombre,"proyecto_id": proyecto.id}
                )
                data = response.json()
                if data.get("success"):
                    # Obtener el case_id del resultado
                    case_id = data["result"].get("caseId") if data.get("result") else None
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}', 'success')
                    if case_id:
                        # Redirigir a cargar_etapa y pasar el case_id y proyecto_id por la URL
                        return redirect(url_for('formulario.cargar_etapa', case_id=case_id, proyecto_id=proyecto.id))
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}', 'success')
                else:
                    flash(f'Error al crear proyecto: {data.get("error")}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            return redirect(url_for('formulario.formulario_nombre'))
        else:
            flash('Por favor, ingresa un nombre válido.', 'error')
    # Obtener case_id y proyecto_id de la URL si existen y pasarlos al template
    case_id = request.args.get('case_id')
    return render_template('formulario_nombre.html', case_id=case_id)

@formulario_bp.route('/cargar_etapa', methods=['GET', 'POST'])
def cargar_etapa():
    if request.method == 'POST':
        case_id = request.form.get('case_id')
        proyecto_id = request.form.get('proyecto_id')
        nombre_etapa = request.form.get('nombre_etapa')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        tipo_cobertura = request.form.get('tipo_cobertura')
        cobertura_solicitada = request.form.get('cobertura_solicitada')
        ultima_etapa = request.form.get('ultima_etapa')

        if proyecto_id and nombre_etapa and fecha_inicio and fecha_fin and tipo_cobertura and cobertura_solicitada:
            try:
                etapa_service.crear_etapa(
                    nombre_etapa,
                    fecha_inicio,
                    fecha_fin,
                    tipo_cobertura,
                    cobertura_solicitada,
                    int(proyecto_id)
                )
                # Enviar datos de la etapa a Bonita
                response = requests.post(
                    url_for('bonita_siguiente.cargar_etapa', _external=True),
                    json={
                        "case_id": case_id,
                        "nombre_etapa": nombre_etapa,
                        "proyecto_id": proyecto_id,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "tipo_cobertura": tipo_cobertura,
                        "cobertura_solicitada": cobertura_solicitada
                    }
                )
                data = response.json()
                if data.get("success"):
                    flash(f'Etapa cargada correctamente para el caso {case_id}', 'success')
                else:
                    flash(f'Error al cargar etapa: {data.get("error")}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            # Si el usuario marcó "ultima_etapa", setear variable en Bonita y redirigir a confirmar
            if ultima_etapa:
                try:
                    # Setear variable ultima_etapa en Bonita a True
                    requests.post(
                        url_for('bonita_siguiente.confirmar_proyecto', _external=True),
                        json={
                            "case_id": case_id,
                            "ultima_etapa": True
                        }
                    )
                    flash('Proyecto confirmado. Se dejó de cargar etapas.', 'success')
                    # Aquí puedes redirigir a la tarea de confirmación si tienes una ruta específica
                    # return redirect(url_for('formulario.confirmar', case_id=case_id, proyecto_id=proyecto_id))
                except Exception as e:
                    flash(f'Error al confirmar proyecto: {str(e)}', 'error')
            return redirect(url_for('formulario.cargar_etapa', case_id=case_id, proyecto_id=proyecto_id))
        else:
            flash('Por favor, completa todos los campos.', 'error')
    # Obtener case_id y proyecto_id de la URL si existen y pasarlos al template
    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')
    return render_template('cargar_etapa.html', case_id=case_id, proyecto_id=proyecto_id)