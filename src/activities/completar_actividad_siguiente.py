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

def completar_tarea_por_nombre(process, case_id, nombre_tarea):
    """Busca, asigna y completa una tarea en Bonita por su nombre"""
    activities = process.search_activity_by_case(case_id)
    task_id = None
    for act in activities:
        if act.get("name") == nombre_tarea:
            task_id = act.get("id")
            break

    if not task_id:
        raise Exception(f"No se encontró la tarea '{nombre_tarea}' para el case {case_id}")

    user = process.get_user_by_name("walter.bates")
    process.assign_task(task_id, user["id"])
    return process.complete_activity(task_id)

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

        # Asignar y completar
        result = completar_tarea_por_nombre(process, case_id, "Cargar etapa")

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

        
        result = completar_tarea_por_nombre(process, case_id, "Confirmar etapas")

        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

@bonita_bp_siguiente.route("/completar_etapa/<int:etapa_id>", methods=["POST"])
def completar_etapa(etapa_id):
    case_id = request.json.get("case_id")
    access = AccessAPI()
    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        result = completar_tarea_por_nombre(process, case_id, "Completar etapa")

        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
    

@bonita_bp_siguiente.route("/completar_ver_proyectos", methods=["POST"])
def completar_ver_proyectos():
    case_id = request.json.get("case_id")
    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        # Usa el helper para completar la tarea
        result = completar_tarea_por_nombre(process, case_id, "Ver proyectos")

        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
    
@bonita_bp_siguiente.route("/completar_seleccionar_proyecto", methods=["POST"])
def completar_seleccionar_proyecto():
    case_id = request.json.get("case_id")
    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        # Usa el helper para completar la tarea
        result = completar_tarea_por_nombre(process, case_id, "Seleccionar proyecto")

        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})