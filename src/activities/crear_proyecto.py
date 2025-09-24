from flask import Blueprint, request, jsonify
from classes.process import Process
from classes.access import AccessAPI

bonita_bp = Blueprint("bonita", __name__, url_prefix="/bonita")




@bonita_bp.route("/iniciar_proceso", methods=["POST"])
def iniciar_proceso():
    access = AccessAPI()
    try:
        token, session = access.login()
        process = Process(session)

        # Nombre del proceso
        process_name = "Proceso de generar proyecto"

        # Variables iniciales (del request)
        nombre = request.json.get("nombre")

        # Obtener ID del proceso
        process_id = process.get_process_id_by_name(process_name)

        # Iniciar instancia
        instance = process.initiate(process_id)
        case_id = instance.get("caseId")

        # Setear variables iniciales
        process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")

        return jsonify({"success": True, "caseId": case_id})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})

@bonita_bp.route("/completar_actividad", methods=["POST"])
def completar_actividad():
    access = AccessAPI()
    nombre = request.json.get("nombre")

    try:
        # 1. Login
        cookie, session = access.login()

        # 2. Instanciar Process con la sesión autenticada
        process = Process(session)

        # 3. Obtener ID del proceso
        process_id = process.get_process_id_by_name("Proceso de generar proyecto")
        print(f"process_id response: {process_id}")

        # 4. Iniciar instancia
        instance = process.initiate(process_id)
        print(f"instance response: {instance}")
        case_id = instance.get("caseId")

        # 5. Setear variables
        set_var_resp = process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")
        print(f"set_variable_by_case response: {set_var_resp}")

        # 6. Buscar actividad
        activities = process.search_activity_by_case(case_id)
        print(f"search_activity_by_case response: {activities}")
        task_id = activities[0].get("id")

        # 7. Buscar usuario genérico
        user = process.get_user_by_name("walter.bates")
        print(f"get_user_by_name response: {user}")

        # 8. Asignar tarea
        assign_resp = process.assign_task(task_id, user["id"])
        print(f"assign_task response: {assign_resp}")

        # 9. Completar actividad
        result = process.complete_activity(task_id)
        print(f"complete_activity response: {result}")

        return jsonify({"success": True, "result": result})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
