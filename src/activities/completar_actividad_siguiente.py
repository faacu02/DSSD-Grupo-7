# services/bonita_service.py

import json
from datetime import datetime
from flask import session, jsonify
import time
from classes.access import AccessAPI
from classes.process import Process

import random
# ============================
#  RECONSTRUIR SESSION DE BONITA
# ============================
def get_process_from_session():
    bonita_cookies = session.get("bonita_cookies")

    if not bonita_cookies:
        raise Exception("Usuario Bonita no logueado.")

    bonita_session = AccessAPI.build_session_from_cookies(bonita_cookies)
    return Process(bonita_session)


# ============================
#  COMPLETAR TAREA POR NOMBRE
# ============================
def completar_tarea_por_nombre(process, case_id, nombre_tarea):
    activities = process.search_activity_by_case(case_id)

    task_id = None
    for act in activities:
        if act.get("name") == nombre_tarea:
            task_id = act.get("id")
            break

    if not task_id:
        raise Exception(f"No se encontró la tarea '{nombre_tarea}' en el case {case_id}")

    # ❌ NO asignar manualmente, Bonita lo hace según ACTOR
    # user = process.get_user_by_name(bonita_username)
    # process.assign_task(task_id, user["id"])

    # ✔ Completar directamente con la sesión del usuario real
    return process.complete_activity(task_id)


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
    user = process.get_user_by_name(session.get("bonita_username"))
    process.assign_task(task_id, user["id"])

    # Completar la tarea
    process.complete_activity(task_id)

    return {
        "task_id": task_id,
        "task_name": task.get("displayName"),
        "technical_name": task.get("name")
    }


# =====================================================
# ============  SERVICIOS PARA BONITA  ================
# =====================================================






# ----------------------------
# Cargar etapa
# ----------------------------
def cargar_etapa(case_id, nombre_etapa, fecha_inicio, fecha_fin, tipo_cobertura, cobertura_solicitada, ultima_etapa):
    process = get_process_from_session()

    if isinstance(cobertura_solicitada, str):
        try:
            cobertura_solicitada = json.loads(cobertura_solicitada)
        except:
            cobertura_solicitada = {"valor": cobertura_solicitada}

    if not isinstance(cobertura_solicitada, dict):
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
    process.set_variable_by_case(case_id, "etapa_data", etapa_json_str, "java.lang.String")

    if ultima_etapa:
        process.set_variable_by_case(case_id, "ultima_etapa", "true", "java.lang.Boolean")

    result = completar_tarea_disponible(process, case_id)

    etapa_cloud_id = process.wait_for_case_variable(case_id, "etapa_cloud_id")

    return {"result": result, "etapa_cloud_id": etapa_cloud_id}


# ----------------------------
# Confirmar proyecto
# ----------------------------
def confirmar_proyecto(case_id, ultima_etapa):
    process = get_process_from_session()

    valor = "true" if ultima_etapa else "false"
    process.set_variable_by_case(case_id, "ultima_etapa", valor, "java.lang.Boolean")

    return completar_tarea_disponible(process, case_id)


# Cargar donación
# ----------------------------
def cargar_donacion(case_id, etapa_id, donante_nombre, monto, especificacion):
    process = get_process_from_session()

    try:
        monto_float = float(monto) if monto else None
    except:
        monto_float = None

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
    process.set_variable_by_case(case_id, "donacion_data", donacion_json_str, "java.lang.String")

    return completar_tarea_disponible(process, case_id)


# ----------------------------
# Ver propuestas por etapa
# ----------------------------
def ver_propuestas(case_id, etapa_id):
    process = get_process_from_session()

    process.set_variable_by_case(case_id, "etapa_id_get", int(etapa_id), "java.lang.Integer")

    completar_tarea_disponible(process, case_id)

    propuestas_raw = process.wait_for_case_variable(case_id, "propuestas_por_etapa")

    return json.loads(propuestas_raw)


# ----------------------------
# Aceptar propuesta
# ----------------------------
def aceptar_propuesta(case_id, propuesta_id):
    process = get_process_from_session()

    process.set_variable_by_case(case_id, "propuesta_aceptar_id", int(propuesta_id), "java.lang.Integer")

    completar_tarea_disponible(process, case_id)

    cobertura_raw = process.wait_for_case_variable(case_id, "cobertura_actual")

    return json.loads(cobertura_raw)


def completar_etapa(case_id, etapa_id, ultima_propuesta):
    try:
        process = get_process_from_session()

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


def esperar_tarea_disponible(process, case_id, intentos=10, delay=0.2):
    for _ in range(intentos):
        tareas = process.search_activity_by_case(case_id)
        if tareas:
            return tareas[0]
        time.sleep(delay)
    return None

def marcar_proyecto_como_completado(case_id):
    try:
        process = get_process_from_session()
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

