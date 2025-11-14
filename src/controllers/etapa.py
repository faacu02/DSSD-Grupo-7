from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from models import etapa
import services.etapa_service as etapa_service
import services.proyecto_servicce as proyecto_service


etapa_bp = Blueprint('etapa', __name__)

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

        if proyecto_id and nombre_etapa and fecha_inicio and fecha_fin and tipo_cobertura and cobertura_solicitada:
            try:
                response = requests.post(
                    url_for('bonita_siguiente.cargar_etapa', _external=True),
                    json={
                        "case_id": case_id,
                        "nombre_etapa": nombre_etapa,
                        "proyecto_id": proyecto_id,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "tipo_cobertura": tipo_cobertura,
                        "cobertura_solicitada": cobertura_solicitada,
                        "ultima_etapa": ultima_etapa
                    }
                )
                data = response.json()

                etapa_cloud_id = data.get("etapa_cloud_id")

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
                flash(f'Error de conexión: {str(e)}', 'error')

            if ultima_etapa == 'true':
                return redirect(url_for('formulario.confirmar_proyecto',
                                        case_id=case_id,
                                        proyecto_id=proyecto_id))

            return redirect(url_for('etapa.cargar_etapa',
                                    case_id=case_id,
                                    proyecto_id=proyecto_id))

    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')

    return render_template('cargar_etapa.html',
                           case_id=case_id,
                           proyecto_id=proyecto_id)


@etapa_bp.route('/ver_etapas/<int:proyecto_id>', methods=['GET'])
def ver_etapas_proyecto(proyecto_id):
    case_id = request.args.get('case_id')

    etapas = etapa_service.obtener_etapas_por_proyecto(proyecto_id)
    proyecto = None
    return render_template('ver_etapas.html', etapas=etapas, proyecto=proyecto, case_id=case_id)


@etapa_bp.route('/detalle_etapa/<int:etapa_id>', methods=['GET'])
def detalle_etapa(etapa_id):
    case_id = request.args.get('case_id')
    etapa = etapa_service.obtener_etapa_por_id(etapa_id)
    etapa_cloud_id = etapa.etapa_cloud_id

    if not etapa:
        flash('Etapa no encontrada.', 'error')

        return redirect(url_for('formulario.ver_proyectos', case_id=case_id))

    return render_template('detalle_etapa.html', etapa=etapa, case_id=case_id, etapa_cloud_id=etapa_cloud_id)


@etapa_bp.route('/completar/<int:etapa_id>', methods=['GET', 'POST'])
def completar_etapa(etapa_id):
    etapa = etapa_service.obtener_etapa_por_id(etapa_id)
    if not etapa:
        flash('Etapa no encontrada.', 'error')
        return redirect(url_for('etapa.ver_etapas_proyecto', proyecto_id=etapa.proyecto_id))

    if request.method == 'POST':
        etapa_service.marcar_etapa_completada(etapa_id)
        flash('Etapa completada correctamente.', 'success')
        return redirect(url_for('etapa.ver_etapas_proyecto', proyecto_id=etapa.proyecto_id))

    return render_template('completar_etapa.html', etapa=etapa)

@etapa_bp.route('/originante/ver_etapas/<int:proyecto_id>', methods=['GET'])
def ver_etapas_ong_originante(proyecto_id):
    case_id = request.args.get('case_id')

    etapas = etapa_service.obtener_etapas_por_proyecto(proyecto_id)
    proyecto = None
    return render_template('ver_etapas_ong_originante.html', etapas=etapas, proyecto=proyecto, case_id=case_id)

