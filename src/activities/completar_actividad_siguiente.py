from multiprocessing import process
from flask import Blueprint, json, request, jsonify
from classes.process import Process
from classes.access import AccessAPI
from datetime import datetime
import json

bonita_bp_siguiente = Blueprint("bonita_siguiente", __name__, url_prefix="/bonita")



def to_timestamp(fecha_str):
    if not fecha_str:
        return None
    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

from flask import Blueprint, request, jsonify
from classes.process import Process
from classes.access import AccessAPI
from datetime import datetime
import json

bonita_bp_siguiente = Blueprint("bonita_siguiente", __name__, url_prefix="/bonita")


def to_timestamp(fecha_str):
    if not fecha_str:
        return None
    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)


@bonita_bp_siguiente.route("/cargar_etapa", methods=["POST"])
def cargar_etapa():
    case_id = request.json.get("case_id")
    nombre_etapa = request.json.get("nombre_etapa")
    proyecto_id = request.json.get("proyecto_id")
    fecha_inicio = request.json.get("fecha_inicio")
    fecha_fin = request.json.get("fecha_fin")
    tipo_cobertura = request.json.get("tipo_cobertura")
    cobertura_solicitada = request.json.get("cobertura_solicitada")
    ultima_etapa = request.json.get("ultima_etapa", False)


    try:    
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        # 🧩 Normalizar cobertura_solicitada
        if isinstance(cobertura_solicitada, str):
            try:
                cobertura_solicitada = json.loads(cobertura_solicitada)
            except json.JSONDecodeError:
                cobertura_solicitada = {"valor": cobertura_solicitada}
        elif not isinstance(cobertura_solicitada, dict):
            cobertura_solicitada = {"valor": str(cobertura_solicitada)}

        # ✅ Armar el JSON limpio para enviar al cloud
        etapa_data = {
            "nombre": nombre_etapa,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tipo_cobertura": tipo_cobertura,
            "proyecto_id": 1,
            "cobertura_solicitada": cobertura_solicitada
        }

        # 💾 Convertir a string JSON limpio
        etapa_json_str = json.dumps(etapa_data, ensure_ascii=False)
        print(f"[DEBUG] Etapa data enviada a Bonita:\n{etapa_json_str}")

        # ✅ Setear variable etapa_data (que el conector usa como payload)
        process.set_variable_by_case(case_id, "etapa_data", etapa_json_str, "java.lang.String")
        print("[DEBUG] Variable etapa_data guardada correctamente en Bonita")


        if ultima_etapa == 'true':
            process.set_variable_by_case(case_id, "ultima_etapa", "true", "java.lang.Boolean")

        # Buscar actividad pendiente
        activities = process.search_activity_by_case(case_id)
        if not activities:
            return jsonify({"success": False, "error": "No se encontraron actividades para el case."})
        task_id = activities[0].get("id")

        # Asignar y completar
        user = process.get_user_by_name("walter.bates")
        process.assign_task(task_id, user["id"])
        result = process.complete_activity(task_id)

        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

@bonita_bp_siguiente.route("/confirmar_proyecto", methods=["POST"])
def confirmar_proyecto():
    case_id = request.json.get("case_id")
    ultima_etapa = request.json.get("ultima_etapa", False)
    try:
        # Usar la sesión existente en lugar de hacer login nuevamente
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        # 2. Setear la variable ultima_etapa en el case
        valor = "true" if ultima_etapa else "false"
        process.set_variable_by_case(case_id, "ultima_etapa", valor, "java.lang.Boolean")

        
        activities = process.search_activity_by_case(case_id)
        task_id = None
        for act in activities:
            if act.get("name") == "Confirmar etapas":  # usa el nombre exacto en Bonita
                task_id = act.get("id")
                break

        if not task_id:
            return jsonify({"success": False, "error": "No se encontró la tarea Confirmar etapas"})

        # 5. Buscar usuario genérico
        user = process.get_user_by_name("walter.bates")
        print(f"get_user_by_name response: {user}")

        # 6. Asignar tarea
        assign_resp = process.assign_task(task_id, user["id"])
        print(f"assign_task response: {assign_resp}")
        

        # 7. Completar actividad
        result = process.complete_activity(task_id)
        print(f"complete_activity response: {result}")

        return jsonify({"success": True})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})