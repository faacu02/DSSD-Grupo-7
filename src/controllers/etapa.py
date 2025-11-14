# controllers/etapa.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import services.etapa_service as etapa_service
import services.proyecto_servicce as proyecto_service

# ⭐ servicios Bonita
from activities.completar_actividad_siguiente import cargar_etapa as bonita_cargar_etapa

etapa_bp = Blueprint('etapa', __name__)


# ==================================================================
#  CARGAR ETAPA  (YA SIN REQUESTS POST)
# ==================================================================
@etapa_bp.route('/completar_etapa', methods=['GET', 'POST'])
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

        if not (proyecto_id and nombre_etapa and fecha_inicio and fecha_fin and tipo_cobertura):
            flash("Faltan campos obligatorios", "error")
            return redirect(url_for('etapa.cargar_etapa',
                                    case_id=case_id,
                                    proyecto_id=proyecto_id))

        try:
            # ⭐ Llamada DIRECTA a Bonita (sin requests.post)
            bonita_result = bonita_cargar_etapa(
                case_id,
                nombre_etapa,
                fecha_inicio,
                fecha_fin,
                tipo_cobertura,
                cobertura_solicitada,
                ultima_etapa,
            )

            etapa_cloud_id = bonita_result.get("etapa_cloud_id")

            # ⭐ Crear etapa en base local
            etapa_service.crear_etapa(
                nombre_etapa,
                fecha_inicio,
                fecha_fin,
                tipo_cobertura,
                cobertura_solicitada,
                int(proyecto_id),
                etapa_cloud_id
            )

        except Exception as e:
            flash(f"Error cargando etapa: {str(e)}", "error")
            return redirect(url_for('etapa.cargar_etapa',
                                    case_id=case_id,
                                    proyecto_id=proyecto_id))

        if ultima_etapa == 'true':
            return redirect(url_for('formulario.confirmar_proyecto',
                                    case_id=case_id,
                                    proyecto_id=proyecto_id))

        return redirect(url_for('etapa.cargar_etapa',
                                case_id=case_id,
                                proyecto_id=proyecto_id))

    # GET
    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')

    return render_template('cargar_etapa.html',
                           case_id=case_id,
                           proyecto_id=proyecto_id)



# ==================================================================
#  VER ETAPAS (ORIGINANTE / INTERVINIENTE)
# ==================================================================
@etapa_bp.route('/ver_etapas/<int:proyecto_id>')
def ver_etapas_proyecto(proyecto_id):
    etapas = etapa_service.obtener_etapas_por_proyecto(proyecto_id)
    case_id = request.args.get("case_id")
    return render_template('ver_etapas.html',
                           etapas=etapas,
                           case_id=case_id,
                           proyecto=None)



@etapa_bp.route('/originante/ver_etapas/<int:proyecto_id>')
def ver_etapas_ong_originante(proyecto_id):
    etapas = etapa_service.obtener_etapas_por_proyecto(proyecto_id)
    case_id = request.args.get("case_id")
    return render_template('ver_etapas_ong_originante.html',
                           etapas=etapas,
                           case_id=case_id)



# ==================================================================
#  DETALLE DE ETAPA
# ==================================================================
@etapa_bp.route('/detalle_etapa/<int:etapa_id>')
def detalle_etapa(etapa_id):
    case_id = request.args.get('case_id')
    etapa_obj = etapa_service.obtener_etapa_por_id(etapa_id)

    if not etapa_obj:
        flash('Etapa no encontrada.', 'error')
        return redirect(url_for('formulario.ver_proyectos'))

    return render_template(
        'detalle_etapa.html',
        etapa=etapa_obj,
        case_id=case_id,
        etapa_cloud_id=etapa_obj.etapa_cloud_id
    )



# ==================================================================
#  COMPLETAR ETAPA LOCAL (MARCAR COMPLETADA)
# ==================================================================
@etapa_bp.route('/completar/<int:etapa_id>', methods=['GET', 'POST'])
def completar_etapa(etapa_id):
    etapa_obj = etapa_service.obtener_etapa_por_id(etapa_id)

    if not etapa_obj:
        flash("Etapa no encontrada", "error")
        return redirect(url_for('formulario.ver_proyectos'))

    if request.method == 'POST':
        etapa_service.marcar_etapa_completada(etapa_id)
        flash("Etapa completada correctamente", "success")
        return redirect(url_for('etapa.ver_etapas_proyecto', proyecto_id=etapa_obj.proyecto_id))

    return render_template('completar_etapa.html', etapa=etapa_obj)
