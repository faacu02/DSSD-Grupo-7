from classes.access import AccessAPI
from classes.process import Process
from flask import session


from classes.access import AccessAPI
from classes.process import Process
from flask import session


def iniciar_proyecto(nombre_proyecto):
    """
    Inicia un proceso en Bonita y completa la tarea inicial
    SIN asignación manual. Bonita valida el actor.
    """

    # Recuperar cookies Bonita de Flask
    bonita_cookies = session.get("bonita_cookies")

    if not bonita_cookies:
        raise Exception("Usuario Bonita no logueado")

    # Reconstruir sesión Bonita
    bonita_session = AccessAPI.build_session_from_cookies(bonita_cookies)
    process = Process(bonita_session)

    # 1️⃣ Obtener ID del proceso
    process_id = process.get_process_id_by_name("Proceso de generar proyecto")

    # 2️⃣ Iniciar caso
    instance = process.initiate(process_id)
    case_id = instance["caseId"]
    print(f"✅ Proceso iniciado con case ID: {case_id}")

    # 3️⃣ Buscar tarea inicial
    import time

    for _ in range(5):
        activities = process.search_activity_by_case(case_id)
        if activities:
            break 
        time.sleep(0.2)
    activities = process.search_activity_by_case(case_id)
    if not activities:
        raise Exception("No se encontró la tarea inicial del proceso")

    task_id = activities[0]["id"]

    # 4️⃣ NO ASIGNAR MANUALMENTE → Bonita valida actor automáticamente
    #    process.assign_task(task_id, ... )  ❌ ELIMINADO

    # 5️⃣ Enviar variable y completar tarea
    print(f"✅ Completando tarea inicial ID: {task_id} con nombre_proyecto='{nombre_proyecto}'")
    process.set_variable_by_case(
        case_id,
        "nombre_proyecto",
        nombre_proyecto,
        "java.lang.String"
    )
    print("Variable 'nombre_proyecto' establecida.")
    user = process.get_user_by_name(session.get("bonita_username"))
    print("Usuario para completar tarea:", user)
    # ✔ Bonita solo permitirá completar si el usuario pertenece al Actor correcto
    process.assign_task(task_id, user["id"])
    result = process.complete_activity(task_id)

    return case_id
