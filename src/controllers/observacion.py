from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from services import etapa_service
from classes.process import Process
from classes.access import AccessAPI
import json

observacion_bp = Blueprint('observacion', __name__)

@observacion_bp.route('/escribir_observacion/<int:etapa_id>', methods=['GET', 'POST'])
def escribir_observacion(etapa_id):
    etapa = etapa_service.obtener_etapa_por_id(etapa_id)
    if not etapa:
        flash('Etapa no encontrada.', 'error')
        return redirect(url_for('formulario.ver_proyectos'))

    proyecto_id = etapa.proyecto_id

    if request.method == 'POST':
        descripcion = request.form.get('descripcion')

        if not descripcion or not descripcion.strip():
            flash('La observación está vacía.', 'error')
            return redirect(url_for('etapa.ver_etapas_proyecto_completado', proyecto_id=proyecto_id))

        flash(f"Observación recibida: {descripcion}", "info")

        """
        try:
            # ----------- INICIO BONITA -------------
            session = AccessAPI.get_bonita_session()
            process = Process(session)

            # 1. Buscar el proceso "Crear observacion"
            process_id = process.get_process_id_by_name("Crear observacion")

            # 2. Iniciar proceso → genera un case
            instance = process.initiate(process_id)
            case_id = instance.get("caseId")

            # 3. Construir el JSON que se enviará como un string
            payload = {
                "etapa_id": etapa.etapa_cloud_id,
                "descripcion": descripcion
            }

            # 4. Mandar el JSON como string a Bonita
            process.set_variable_by_case(
                case_id,
                "payload_observacion",         # nombre de la variable en Bonita
                json.dumps(payload),           # lo convertimos a string JSON
                "java.lang.String"
            )

            # 5. Buscar actividades pendientes
            activities = process.search_activity_by_case(case_id)
            if not activities:
                flash("No hay tareas pendientes en el proceso de observación.", "error")
                return redirect(url_for('etapa.ver_etapas_proyecto_completado', proyecto_id=proyecto_id))

            task_id = activities[0]["id"]

            # 6. Asignar la tarea a walter.bates
            user = process.get_user_by_name("walter.bates")
            process.assign_task(task_id, user["id"])

            # 7. Completar la actividad
            process.complete_activity(task_id)

            # ----------- FIN BONITA --------------

            flash("Observación enviada correctamente a Bonita.", "success")

        except Exception as e:
            print("Error Bonita:", e)
            flash("Error al enviar la observación a Bonita.", "error")

        """
        return redirect(url_for('etapa.ver_etapas_proyecto_completado', proyecto_id=proyecto_id))

    return render_template('escribir_observacion.html', etapa=etapa, proyecto_id=proyecto_id)