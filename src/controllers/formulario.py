from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import services.proyecto_servicce as proyecto_service
from datetime import datetime
from classes.access import AccessAPI
from classes.process import Process
from activities.crear_proyecto import iniciar_proyecto, iniciar_proyecto_en_curso
from activities.completar_actividad_siguiente import marcar_proyecto_como_completado as bonita_marcar_como_completado
from utils.hasRol import roles_required

formulario_bp = Blueprint('formulario', __name__)


@formulario_bp.route('/')
def root():
    """Ruta raíz - redirige al login o al index según el estado de sesión"""
    if session.get('bonita_username'):
        return redirect(url_for('formulario.index'))
    return redirect(url_for('login.login'))


@formulario_bp.route('/index')
def index():
    case_id = request.args.get('case_id')
    session_roles= session.get("bonita_roles", [])
    return render_template('index.html', case_id=case_id, roles=session_roles)

def to_timestamp(fecha_str):
    if not fecha_str:
        return None
    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)


# ---------------------------------------------------------------------
# ⭐ OPCIÓN 1 → Sin requests internos, llamando a Bonita DIRECTO
# ---------------------------------------------------------------------
@formulario_bp.route('/formulario_nombre', methods=['GET', 'POST'])
@roles_required("Originante")
def formulario_nombre():
    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if not nombre:
            flash('Por favor, ingresa un nombre válido.', 'error')
            return redirect(url_for('formulario.formulario_nombre'))

        try:
            # Crear proyecto local
            proyecto = proyecto_service.crear_proyecto(nombre)
            id_proyecto = proyecto.id

            # ⭐ MODULARIZADO → llamar servicio Bonita
            case_id = iniciar_proyecto(nombre)
            
            proyecto_service.actualizar_case_id(id_proyecto, case_id)

            flash(f"Proyecto creado correctamente: {nombre}", "success")
            return redirect(url_for('etapa.cargar_etapa', case_id=case_id, proyecto_id=proyecto.id))

        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('formulario.formulario_nombre'))
    case_id = request.args.get('case_id')
    return render_template('formulario_nombre.html', case_id=case_id)


# ---------------------------------------------------------------------
# ❗ En OPCIÓN 1, este endpoint NO usa requests internos.
#    Lo reescribiremos cuando adaptemos bonito_siguiente.
# ---------------------------------------------------------------------
@formulario_bp.route('/confirmar_proyecto', methods=['GET', 'POST'])
@roles_required("Originante")
def confirmar_proyecto():
    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')

    # 🔹 GET → solo mostrar la vista
    if request.method == 'GET':
        return render_template('confirmar_proyecto.html',
                               case_id=case_id,
                               proyecto_id=proyecto_id)

    # 🔹 POST → Confirmar en Bonita (ahora SÍ)
    ultima_etapa = True  # porque tu formulario ya lo sabe

    try:
        from activities.completar_actividad_siguiente import confirmar_proyecto as bonita_confirmar

        bonita_confirmar(case_id, ultima_etapa)

        flash('Proyecto confirmado correctamente.', 'success')

        return redirect(url_for('formulario.ver_proyectos', case_id=case_id))

    except Exception as e:
        flash(f"Error confirmando proyecto: {str(e)}", "error")
        return redirect(request.url)


@formulario_bp.route('/proyectos', methods=['GET'])
def ver_proyectos():
    proyectos = proyecto_service.obtener_proyectos()
    case_id = request.args.get('case_id')
    roles = session.get("bonita_roles", [])
    return render_template('ver_proyectos.html', proyectos=proyectos, case_id=case_id, roles=roles)


@formulario_bp.route('/marcar_como_completado/<int:proyecto_id>', methods=['POST'])
def marcar_como_completado(proyecto_id):
    case_id = request.form.get('case_id')
    try:
        proyecto_service.marcar_proyecto_como_completado(proyecto_id)
        # ⭐ Llamada DIRECTA a Bonita (sin requests)
        data = bonita_marcar_como_completado(case_id)
        if data.get("success"):
            flash('Proyecto marcado como completado correctamente.', 'success')
        else:
            flash(f'Error al completar proyecto: {data.get("error")}', 'error')
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'error')

    return redirect(url_for('formulario.ver_proyectos', case_id=case_id))

@formulario_bp.route('/completados', methods=['GET'])
def ver_proyectos_completados():
    roles = session.get("bonita_roles", [])
    is_originante = any(r.lower() == "originante" for r in roles)
    is_interviniente = any(r.lower() == "interviniente" for r in roles)
    try:
        if is_interviniente:
            case_id = request.args.get('case_id')
        else:
            case_id = None
        proyectos = proyecto_service.obtener_proyectos_completados()

        return render_template('ver_proyectos_completados.html',
                               proyectos=proyectos,
                               case_id=case_id)

    except Exception as e:
        flash(f"Error al cargar proyectos completados: {str(e)}", "error")
        return redirect(url_for('formulario.index'))

@formulario_bp.route('/iniciar_proceso_completados')
def iniciar_proceso_completados():
    try:
        case_id = iniciar_proyecto_en_curso()

        # Redirigís al portal o a la bandeja local
        return redirect(url_for("formulario.ver_proyectos_completados", case_id=case_id))

    except Exception as e:
        print("exception", str(e))
        flash(f"Error iniciando proceso en Bonita: {str(e)}", "error")
        return redirect(url_for('formulario.index'))
