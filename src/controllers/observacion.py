from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from classes.access import AccessAPI
from activities.completar_actividad_siguiente import cargar_observacion as bonita_cargar_observacion
from activities.completar_actividad_siguiente import obtener_observaciones_por_etapa
from activities.completar_actividad_siguiente import seleccionar_observacion
from activities.completar_actividad_siguiente import resolver_observacion
import json
from services.etapa_service import obtener_etapa_por_id
observacion_bp = Blueprint('observacion', __name__)

@observacion_bp.route('/cargar_observacion', methods=['GET', 'POST'])
def cargar_observacion():
    etapa_id = request.args.get("etapa_id") or request.form.get("etapa_id")
    case_id = request.args.get("case_id") or request.form.get("case_id")
    etapa= obtener_etapa_por_id(etapa_id)
    if request.method == "POST":
        observacion = request.form.get("observacion")

        bonita_cargar_observacion(case_id, etapa.etapa_cloud_id, observacion)

        flash("Observación cargada correctamente", "success")
        return redirect(url_for("formulario.ver_proyectos_completados", case_id=case_id))

    return render_template("cargar_observacion.html",
                           etapa_id=etapa_id,
                           case_id=case_id)

@observacion_bp.route('/ver_observaciones/', methods=['GET'])
def ver_observaciones_por_etapa():
    etapa_id = request.args.get("etapa_id") or request.form.get("etapa_id")
    case_id = request.args.get("case_id") or request.form.get("case_id")
    etapa = obtener_etapa_por_id(etapa_id)
    response = obtener_observaciones_por_etapa(case_id, etapa.etapa_cloud_id)

    data = response.get_json()
    observaciones = data.get("observaciones", [])

    return render_template(
        "ver_observaciones.html",
        etapa=etapa,
        observaciones=observaciones,
        case_id=case_id
    )

@observacion_bp.route('/detalle_observacion/<observacion_id>', methods=['GET'])
def detalle_observacion(observacion_id):
    case_id = request.args.get("case_id") or request.form.get("case_id")
    etapa_id = request.args.get("etapa_id") or request.form.get("etapa_id")
    etapa = obtener_etapa_por_id(etapa_id)

    response = seleccionar_observacion(case_id, observacion_id)

    data = response.get_json()
    observacion = data.get("observacion", [])

    return render_template(
        "detalle_observacion.html",
        etapa=etapa,
        observacion=observacion,
        case_id=case_id
    )

@observacion_bp.route('/resolver/<observacion_id>', methods=['POST'])
def resolver(observacion_id):
    case_id = session.get("case_id")
    etapa_id = session.get("etapa_id")
    etapa = obtener_etapa_por_id(etapa_id)
    observacion = session.get("observacion")

    resolver_observacion(case_id, observacion_id)

    flash("Observación resuelta correctamente", "success")
    observacion.resuelta = True
    return render_template(
        "detalle_observacion.html",
        etapa=etapa,
        observacion=observacion,
        case_id=case_id
    )