# services/bonita_service.py

import json
from datetime import datetime
from flask import session
from classes.access import AccessAPI
from classes.process import Process


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



# =====================================================
# ============  SERVICIOS PARA BONITA  ================
# =====================================================


# ----------------------------
# Crear proyecto (primer tarea)
# ----------------------------
def crear_proyecto_bonita(nombre, proyecto_id):
    process =  get_process_from_session()

    process_id = process.get_process_id_by_name("Proceso de generar proyecto")
    instance = process.initiate(process_id)
    case_id = instance.get("caseId")

    process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")
    process.set_variable_by_case(case_id, "proyecto_id", proyecto_id, "java.lang.Integer")

    result = completar_tarea_por_nombre(process, case_id, "Cargar nombre proyecto")

    return case_id



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
        "proyecto_id": 1,
        "cobertura_solicitada": cobertura_solicitada
    }

    etapa_json_str = json.dumps(etapa_data, ensure_ascii=False)
    process.set_variable_by_case(case_id, "etapa_data", etapa_json_str, "java.lang.String")

    if ultima_etapa:
        process.set_variable_by_case(case_id, "ultima_etapa", "true", "java.lang.Boolean")

    result = completar_tarea_por_nombre(process, case_id, "Cargar etapa")

    etapa_cloud_id = process.wait_for_case_variable(case_id, "etapa_cloud_id")

    return {"result": result, "etapa_cloud_id": etapa_cloud_id}


# ----------------------------
# Confirmar proyecto
# ----------------------------
def confirmar_proyecto(case_id, ultima_etapa):
    process = get_process_from_session()

    valor = "true" if ultima_etapa else "false"
    process.set_variable_by_case(case_id, "ultima_etapa", valor, "java.lang.Boolean")

    return completar_tarea_por_nombre(process, case_id, "Confirmar etapas")


# ----------------------------
# Completar etapa (botón siguiente etapa)
# ----------------------------
def completar_etapa(case_id):
    process = get_process_from_session()

    return completar_tarea_por_nombre(process, case_id, "Completar etapa")


# ----------------------------
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

    return completar_tarea_por_nombre(process, case_id, "Proponer donación")


# ----------------------------
# Ver propuestas por etapa
# ----------------------------
def ver_propuestas(case_id, etapa_id):
    process = get_process_from_session()

    process.set_variable_by_case(case_id, "etapa_id_get", int(etapa_id), "java.lang.Integer")

    completar_tarea_por_nombre(process, case_id, "Ver propuestas")
    propuestas_raw = process.wait_for_case_variable(case_id, "propuestas_por_etapa")

    return json.loads(propuestas_raw)


# ----------------------------
# Aceptar propuesta
# ----------------------------
def aceptar_propuesta(case_id, propuesta_id):
    process = get_process_from_session()

    process.set_variable_by_case(case_id, "propuesta_aceptar_id", int(propuesta_id), "java.lang.Integer")

    completar_tarea_por_nombre(process, case_id, "Aceptar propuesta")
    cobertura_raw = process.wait_for_case_variable(case_id, "cobertura_actual")

    return json.loads(cobertura_raw)
