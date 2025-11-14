# controllers/donacion.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json

import services.etapa_service as etapa_service

# ⭐ Importamos servicios Bonita
from activities.completar_actividad_siguiente import (
    cargar_donacion as bonita_cargar_donacion,
    ver_propuestas as bonita_ver_propuestas,
    aceptar_propuesta as bonita_aceptar_propuesta
)

donacion_bp = Blueprint('donacion', __name__)


# ===================================================================
#       CARGAR DONACIÓN (LOCAL + BONITA)
# ===================================================================
@donacion_bp.route('/cargar_donacion', methods=['GET', 'POST'])
def cargar_donacion():
    case_id = request.args.get('case_id')
    etapa_id = request.args.get('etapa_id')

    etapa = etapa_service.obtener_etapa_por_id(etapa_id)
    etapa_cloud_id = etapa.etapa_cloud_id if etapa else None
    tipo_cobertura = etapa.tipo_cobertura if etapa else None

    if request.method == 'POST':
        donante_nombre = request.form.get('donante_nombre')
        monto = request.form.get('monto', 0)
        especificacion_raw = request.form.get('especificacion')

        # Normalizar especificacion JSON
        try:
            especificacion = json.loads(especificacion_raw) if especificacion_raw else None
        except json.JSONDecodeError:
            especificacion = {"detalle": especificacion_raw}

        # Validar monto
        try:
            monto_float = float(monto) if monto else None
        except ValueError:
            flash("El monto debe ser un número válido.", "error")
            return redirect(request.url)

        try:
            # ⭐ Llamada DIRECTA al servicio Bonita (sin requests)
            bonita_cargar_donacion(
                case_id,
                etapa_cloud_id,
                donante_nombre,
                monto_float,
                especificacion
            )

            flash("Donación cargada correctamente.", "success")
            return redirect(url_for('formulario.index'))

        except Exception as e:
            flash(f"Error al cargar donación: {str(e)}", "error")

    return render_template(
        'cargar_donacion.html',
        case_id=case_id,
        etapa_id=etapa_id,
        etapa_cloud_id=etapa_cloud_id,
        tipo_cobertura=tipo_cobertura
    )



# ===================================================================
#       VER PROPUESTAS DE UNA ETAPA
# ===================================================================
@donacion_bp.route('/ver_propuestas/<int:etapa_id>')
def ver_propuestas(etapa_id):
    case_id = request.args.get('case_id')

    etapa = etapa_service.obtener_etapa_por_id(etapa_id)

    try:
        # ⭐ Directo al servicio Bonita
        propuestas = bonita_ver_propuestas(case_id, etapa.etapa_cloud_id)

    except Exception as e:
        flash(f"Error recuperando propuestas: {str(e)}", "error")
        return redirect(url_for('etapa.detalle_etapa', etapa_id=etapa_id))

    # propuestas viene como lista/dict, ya no como JSON string
    propuestas_lista = propuestas.get("propuestas", [])

    return render_template(
        'ver_propuestas.html',
        propuestas=propuestas_lista,
        case_id=case_id,
        etapa_id=etapa_id
    )



# ===================================================================
#       ACEPTAR PROPUESTA
# ===================================================================
@donacion_bp.route('/aceptar_propuesta/<int:propuesta_id>')
def aceptar_propuesta(propuesta_id):
    case_id = request.args.get('case_id')
    etapa_id = request.args.get('etapa_id')

    try:
        # ⭐ Llamada directa a Bonita
        cobertura_actual = bonita_aceptar_propuesta(case_id, propuesta_id)

        # Actualizar etapa local
        etapa_service.actualizar_cobertura(etapa_id, cobertura_actual)

        flash("Propuesta aceptada correctamente.", "success")

    except Exception as e:
        flash("Error al aceptar propuesta: " + str(e), "error")

    return redirect(url_for(
        'etapa.detalle_etapa',
        etapa_id=etapa_id,
        case_id=case_id
    ))
