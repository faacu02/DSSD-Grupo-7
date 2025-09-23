from flask import Blueprint, request, jsonify
from classes.process import Process

bonita_bp = Blueprint("bonita", __name__, url_prefix="/bonita")

@bonita_bp.route("/completar_actividad", methods=["POST"])
def completar_actividad():
    nombre = request.json.get("nombre")

    try:
        # 1. Obtener ID del proceso
        process_id = Process.get_process_id("Proceso de generar proyecto")

        # 2. Iniciar instancia
        instance = Process.initiate_process(process_id)
        case_id = instance["caseId"]

        # 3. Setear variables
        Process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "String")

        # 4. Buscar actividad
        activities = Process.search_activity_by_case(case_id)
        task_id = activities[0]["id"]

        # 5. Buscar usuario genérico
        user = Process.get_user_by_name("bates")

        # 6. Asignar tarea
        Process.assign_task(task_id, user["id"])

        # 7. Completar actividad
        result = Process.complete_activity(task_id)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
