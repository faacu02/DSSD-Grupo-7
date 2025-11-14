from classes.access import AccessAPI
from classes.process import Process
from flask import session


def iniciar_proyecto(nombre_proyecto):
    """
    Inicia un proceso en Bonita, asigna la tarea inicial y la completa.
    Devuelve el case_id del proceso.
    """

    # Recuperar cookies Bonita de Flask
    bonita_cookies = session.get("bonita_cookies")
    bonita_username = session.get("bonita_username")

    if not bonita_cookies or not bonita_username:
        raise Exception("Usuario Bonita no logueado")

    # Reconstruir sesión Bonita
    bonita_session = AccessAPI.build_session_from_cookies(bonita_cookies)
    process = Process(bonita_session)

    # 1️⃣ Obtener ID del proceso
    process_id = process.get_process_id_by_name("Proceso de generar proyecto")

    # 2️⃣ Iniciar caso
    instance = process.initiate(process_id)
    case_id = instance["caseId"]

    # 3️⃣ Buscar tarea inicial
    activities = process.search_activity_by_case(case_id)
    task_id = activities[0]["id"]

    # 4️⃣ Asignar tarea al usuario actual
    bonita_user = process.get_user_by_name(bonita_username)
    process.assign_task(task_id, bonita_user["id"])

    # 5️⃣ Enviar variable y completar tarea
    process.set_variable_by_case(case_id, "nombre_proyecto", nombre_proyecto, "java.lang.String")
    process.complete_activity(task_id)

    return case_id
