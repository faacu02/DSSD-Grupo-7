from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
from activities.completar_actividad_siguiente import crear_respuesta as bonita_crear_respuesta
from utils.hasRol import roles_required
respuesta_bp = Blueprint('respuesta', __name__)

@respuesta_bp.route('/crear_respuesta/<int:observacion_id>', methods=['GET', 'POST'])
@roles_required('Originante')
def crear_respuesta(observacion_id):
    case_id = request.args.get("case_id") or request.form.get("case_id")
    cantidad_observaciones = request.args.get("cantidad_observaciones") or request.form.get("cantidad_observaciones")
    proyecto_id = request.args.get("proyecto_id") or request.form.get("proyecto_id")
    print("Cantidad de observaciones pendientes:", cantidad_observaciones)
    etapa_id = request.args.get("etapa_id") or request.form.get("etapa_id")
    print("Etapa ID:", etapa_id)
    if request.method == "POST":
        respuesta_texto = request.form.get("respuesta")
        cantidad_observaciones = int(cantidad_observaciones) - 1
        bonita_crear_respuesta(case_id, observacion_id, respuesta_texto, cantidad_observaciones)

        flash("Respuesta creada correctamente", "success")
        if cantidad_observaciones > 0:
            return redirect(url_for('observacion.ver_observaciones_por_etapa', etapa_id=etapa_id, case_id=case_id, proyecto_id=proyecto_id))
        return redirect(url_for("formulario.index", case_id=case_id))

    return render_template("cargar_respuesta.html",
                           observacion_id=observacion_id,
                           case_id=case_id,
                           cantidad_observaciones=cantidad_observaciones,
                           proyecto_id=proyecto_id,
                           etapa_id=etapa_id)
