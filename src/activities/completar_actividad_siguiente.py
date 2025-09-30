from multiprocessing import process
from flask import Blueprint, request, jsonify
from classes.process import Process
from classes.access import AccessAPI
from datetime import datetime


bonita_bp_siguiente = Blueprint("bonita_siguiente", __name__, url_prefix="/bonita")



def to_timestamp(fecha_str):
    if not fecha_str:
        return None
    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

@bonita_bp_siguiente.route("/cargar_etapa", methods=["POST"])
def cargar_etapa():
    access = AccessAPI()
    # Recibe el case_id y los datos necesarios para la tarea
    case_id = request.json.get("case_id")
    nombre_etapa = request.json.get("nombre_etapa")
    proyecto_id = request.json.get("proyecto_id")
    fecha_inicio = request.json.get("fecha_inicio")
    fecha_fin = request.json.get("fecha_fin")
    tipo_cobertura = request.json.get("tipo_cobertura")
    cobertura_solicitada = request.json.get("cobertura_solicitada")
    #cobertura_actual = request.json.get("cobertura_actual")

    fecha_inicio_ts = to_timestamp(fecha_inicio)
    fecha_fin_ts = to_timestamp(fecha_fin)

    try:
        # 1. Login
        cookie, session = access.login()

        # 2. Instanciar Process con la sesión autenticada
        process = Process(session)

        etapa_data = {
            "nombre": nombre_etapa,
            "fecha_inicio": fecha_inicio_ts,
            "fecha_fin": fecha_fin_ts,
            "tipo_cobertura": tipo_cobertura,
            "cobertura_solicitada": cobertura_solicitada,
            "proyecto_id": int(proyecto_id)
        }

        url = "http://localhost:8080/bonita/API/bdm/businessData/Etapa"
        headers = {
            "X-Bonita-API-Token": session.cookies.get("X-Bonita-API-Token")
        }
        resp = session.post(url, json=etapa_data, headers=headers)
        resp.raise_for_status()
        nueva_etapa = resp.json()
        print(f"Etapa creada en BDM: {nueva_etapa}")


        # 4. Buscar actividad pendiente en el case
        activities = process.search_activity_by_case(case_id)
        print(f"search_activity_by_case response: {activities}")
        if not activities:
            return jsonify({"success": False, "error": "No se encontraron actividades para el case."})
        task_id = activities[0].get("id")

        # 5. Buscar usuario genérico
        user = process.get_user_by_name("walter.bates")
        print(f"get_user_by_name response: {user}")

        # 6. Asignar tarea
        assign_resp = process.assign_task(task_id, user["id"])
        print(f"assign_task response: {assign_resp}")

        # 7. Completar actividad
        result = process.complete_activity(task_id)
        print(f"complete_activity response: {result}")

        return jsonify({"success": True, "result": result})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

@bonita_bp_siguiente.route("/confirmar_proyecto", methods=["POST"])
def confirmar_proyecto():
    access = AccessAPI()
    case_id = request.json.get("case_id")
    ultima_etapa = request.json.get("ultima_etapa", False)

    try:
        # 1. Login
        cookie, session = access.login()
        process = Process(session)

        # 2. Setear la variable ultima_etapa en el case
        process.set_variable_by_case(case_id, "ultima_etapa", bool(ultima_etapa), "java.lang.Boolean")

        return jsonify({"success": True})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})