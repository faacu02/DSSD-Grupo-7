from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import services.proyecto_servicce as proyecto_service
import services.etapa_service as etapa_service
from datetime import datetime
from classes.access import AccessAPI

# Crear el Blueprint
formulario_bp = Blueprint('formulario', __name__)



@formulario_bp.route('/')
def root():
    """Ruta raíz - redirige al login o al index según el estado de sesión"""
    if session.get('logged'):
        return redirect(url_for('formulario.index'))
    return redirect(url_for('login.login'))

@formulario_bp.route('/index')
def index():
    """Página de inicio de ProjectPlanning"""
    return render_template('index.html')


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
                        return redirect(url_for('etapa.cargar_etapa', case_id=case_id, proyecto_id=proyecto.id))
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


@formulario_bp.route('/confirmar_proyecto', methods=['GET', 'POST'])
def confirmar_proyecto():
    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')
    if request.method == 'POST':
        try:
            response = requests.post(
                url_for('bonita_siguiente.confirmar_proyecto', _external=True),
                json={"case_id": case_id, "ultima_etapa": True}
            )
            data = response.json()
            if data.get("success"):
                flash('Proyecto confirmado correctamente.', 'success')
                # 🔹 Redirigir a la lista de proyectos, pasando el case_id
                return redirect(url_for('formulario.ver_proyectos', case_id=case_id))
            else:
                flash(f'Error al confirmar: {data.get("error")}', 'error')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'error')

    return render_template('confirmar_proyecto.html',
                           case_id=case_id,
                           proyecto_id=proyecto_id)


@formulario_bp.route('/proyectos', methods=['GET'])
def ver_proyectos():
    case_id = request.args.get('case_id')

    proyectos = proyecto_service.obtener_proyectos()

    return render_template('ver_proyectos.html', proyectos=proyectos, case_id=case_id)

@formulario_bp.route('/proyectos/completados', methods=['GET'])
def proyectos_completados():
    proyectos = proyecto_service.obtener_proyectos_completados()
    return render_template('proyectos_completados.html', proyectos=proyectos)
