from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
from activities.completar_actividad_siguiente import crear_respuesta as bonita_crear_respuesta

respuesta_bp = Blueprint('respuesta', __name__)

@respuesta_bp.route('/crear_respuesta/<observacion_id>', methods=['GET', 'POST'])
def crear_respuesta(observacion_id):
    case_id = request.args.get("case_id") or request.form.get("case_id")

    if request.method == "POST":
        respuesta_texto = request.form.get("respuesta")

        # Asegurarnos de pasar un entero cuando sea posible
        try:
            observacion_int = int(observacion_id)
        except Exception:
            observacion_int = observacion_id

        bonita_crear_respuesta(case_id, observacion_int, respuesta_texto)

        flash("Respuesta creada correctamente", "success")
        return redirect(url_for("formulario.ver_proyectos_completados", case_id=case_id))

    return render_template("cargar_respuesta.html",
                           observacion_id=observacion_id,
                           case_id=case_id)
