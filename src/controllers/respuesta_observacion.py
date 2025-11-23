from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
from activities.completar_actividad_siguiente import crear_respuesta as bonita_crear_respuesta
from utils.hasRol import roles_required
respuesta_bp = Blueprint('respuesta', __name__)

@respuesta_bp.route('/crear_respuesta/<int:observacion_id>', methods=['GET', 'POST'])

@roles_required('Originante')
def crear_respuesta(observacion_id):
    case_id = request.args.get("case_id") or request.form.get("case_id")

    if request.method == "POST":
        respuesta_texto = request.form.get("respuesta")

        bonita_crear_respuesta(case_id, observacion_id, respuesta_texto)

        return redirect(url_for("formulario.ver_proyectos_completados", case_id=case_id, success="Respuesta creada correctamente."))

    return render_template("cargar_respuesta.html",
                           observacion_id=observacion_id,
                           case_id=case_id)
