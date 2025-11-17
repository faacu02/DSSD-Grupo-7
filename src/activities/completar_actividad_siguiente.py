from multiprocessing import process
from flask import Blueprint, json, request, jsonify
from classes.process import Process
from classes.access import AccessAPI
from datetime import datetime, time
import json
import time
import random
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

        if isinstance(cobertura_solicitada, str):
            try:
                cobertura_solicitada = json.loads(cobertura_solicitada)
            except json.JSONDecodeError:
                cobertura_solicitada = {"valor": cobertura_solicitada}
        elif not isinstance(cobertura_solicitada, dict):
            cobertura_solicitada = {"valor": str(cobertura_solicitada)}

        etapa_data = {
            "nombre": nombre_etapa,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tipo_cobertura": tipo_cobertura,
            "proyecto_id": random.randint(1, 3),
            "cobertura_solicitada": cobertura_solicitada
        }

        etapa_json_str = json.dumps(etapa_data, ensure_ascii=False)
        print(f"[DEBUG] Etapa data enviada a Bonita:\n{etapa_json_str}")

        process.set_variable_by_case(case_id, "etapa_data", etapa_json_str, "java.lang.String")
        print("[DEBUG] Variable etapa_data guardada correctamente en Bonita")


        if ultima_etapa == 'true':
            process.set_variable_by_case(case_id, "ultima_etapa", "true", "java.lang.Boolean")

        result = completar_tarea_disponible(process, case_id)
        etapa_cloud_id = process.wait_for_case_variable(case_id, "etapa_cloud_id")
        print("[DEBUG] etapa_cloud_id recuperado:", etapa_cloud_id)

        return jsonify({
            "success": True,
            "result": result,
            "etapa_cloud_id": etapa_cloud_id
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

@bonita_bp_siguiente.route("/confirmar_proyecto", methods=["POST"])
def confirmar_proyecto():
    case_id = request.json.get("case_id")
    ultima_etapa = request.json.get("ultima_etapa", False)
    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        valor = "true" if ultima_etapa else "false"
        process.set_variable_by_case(case_id, "ultima_etapa", valor, "java.lang.Boolean")

        
        result = completar_tarea_disponible(process, case_id)

        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

    
@bonita_bp_siguiente.route("/cargar_donacion", methods=["POST"])
def cargar_donacion():
    case_id = request.json.get("case_id")
    etapa_id = request.json.get("etapa_id")
    donante_nombre = request.json.get("donante_nombre")
    monto = request.json.get("monto")
    especificacion = request.json.get("especificacion")  
    
    try:
        monto_float = float(monto) if monto else None

        session = AccessAPI.get_bonita_session()
        process = Process(session)

        if isinstance(especificacion, str):
            try:
                especificacion = json.loads(especificacion)
            except:
                especificacion = {"detalle": especificacion}

        if not isinstance(especificacion, dict):
            especificacion = {"detalle": str(especificacion)}

        donacion_data = {
            "etapa_id": etapa_id,
            "monto": monto_float,
            "especificacion": especificacion,
            "donante_nombre": donante_nombre,
        }

        donacion_json_str = json.dumps(donacion_data, ensure_ascii=False)
        print(f"[DEBUG] Donación data enviada a Bonita:\n{donacion_json_str}")

        process.set_variable_by_case(case_id, "donacion_data", donacion_json_str, "java.lang.String")
        print("[DEBUG] Variable donacion_data guardada correctamente en Bonita")

        result = completar_tarea_disponible(process, case_id)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

@bonita_bp_siguiente.route("/ver_propuestas", methods=["GET"])
def ver_propuestas():
    case_id = request.args.get("case_id")
    etapa_id = request.args.get("etapa_id")
    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        process.set_variable_by_case(case_id, "etapa_id_get", int(etapa_id), "java.lang.Integer")
        result = completar_tarea_disponible(process, case_id)
        propuestas = process.wait_for_case_variable(case_id, "propuestas_por_etapa")


        return jsonify({"success": True, "propuestas": propuestas})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
    
@bonita_bp_siguiente.route('/aceptar_propuesta', methods=['POST'])
def aceptar_propuesta():
    case_id = request.json.get('case_id')
    propuesta_id = request.json.get('propuesta_id')

    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        process.set_variable_by_case(case_id, "propuesta_aceptar_id", int(propuesta_id), "java.lang.Integer")

        result = completar_tarea_disponible(process, case_id)

        cobertura_actual_raw = process.wait_for_case_variable(case_id, "cobertura_actual")
        cobertura_actual = json.loads(cobertura_actual_raw)
        return jsonify({"success": True, "result": result, "cobertura_actual": cobertura_actual})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
    
@bonita_bp_siguiente.route('/completar_etapa', methods=['POST'])
def completar_etapa():
    case_id = request.json.get('case_id')
    etapa_id = request.json.get('etapa_id')
    ultima_propuesta = request.json.get('ultima_propuesta', False)

    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        if ultima_propuesta == 'true':
            if isinstance(ultima_propuesta, str):
                 ultima_propuesta = ultima_propuesta.lower() == "true"
            process.set_variable_by_case(case_id, "ultima_propuesta", "true", "java.lang.Boolean")

        primera = completar_tarea_disponible(process, case_id)

        # 2️⃣ Esperar que Bonita cree "Completar etapa"
        time.sleep(0.3)

        # 3️⃣ Completar "Completar etapa"
        process.set_variable_by_case(case_id, "etapa_a_completar_id", int(etapa_id), "java.lang.Integer")
        segunda = completar_tarea_disponible(process, case_id)

        return jsonify({"success": True, "result": segunda})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

def completar_tarea_disponible(process, case_id):
    """
    Busca la tarea humana disponible para el case y la completa,
    sin importar el nombre.
    """
    # Buscar actividades disponibles
    activities = process.search_activity_by_case(case_id)
    if not activities:
        raise Exception(f"No hay tareas disponibles para el case {case_id}")

    # Tomar la primera tarea disponible
    task = activities[0]
    task_id = task["id"]

    # Asignar al usuario actual (Walter)
    user = process.get_user_by_name("walter.bates")
    process.assign_task(task_id, user["id"])

    # Completar la tarea
    process.complete_activity(task_id)

    return {
        "task_id": task_id,
        "task_name": task.get("displayName"),
        "technical_name": task.get("name")
    }

def esperar_tarea_disponible(process, case_id, intentos=10, delay=0.2):
    for _ in range(intentos):
        tareas = process.search_activity_by_case(case_id)
        if tareas:
            return tareas[0]
        time.sleep(delay)
    return None

@bonita_bp_siguiente.route('/marcar_como_completado', methods=['POST'])
def marcar_proyecto_como_completado():
    case_id = request.json.get('case_id')

    try:
        session = AccessAPI.get_bonita_session()
        process = Process(session)
        process.set_variable_by_case(case_id, "ultima_etapa_a_completar", "true", "java.lang.Boolean")


        primera = completar_tarea_disponible(process, case_id)

        # 2️⃣ Esperar que Bonita cree "Completar etapa"
        time.sleep(0.3)

        # 3️⃣ Completar "Completar etapa"
        segunda = completar_tarea_disponible(process, case_id)

        return jsonify({"success": True, "result": segunda})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})