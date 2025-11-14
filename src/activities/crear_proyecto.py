from flask import Blueprint, request, jsonify, session
from classes.process import Process

bonita_bp = Blueprint("bonita", __name__, url_prefix="/bonita")

@bonita_bp.route("/completar_actividad", methods=["POST"])
def completar_actividad():
    try:
        nombre = request.json.get("nombre")

        print("Cookies HTTP recibidas:", request.cookies)

        # Convertir cookies HTTP a dict normal
        bonita_cookies = request.cookies.to_dict()
        bonita_username = request.json.get("bonita_username")

        if not bonita_cookies or not bonita_username:
            return jsonify({"success": False, "error": "Usuario Bonita no logueado"}), 401

        # Crear sesión de requests con las cookies de Bonita
        import requests
        session_bonita = requests.Session()
        session_bonita.cookies.update(bonita_cookies)

        # Crear Process correctamente
        process = Process(session_bonita)
        # 1️⃣ Obtener ID del proceso
        process_id = process.get_process_id_by_name("Proceso de generar proyecto")

        # 2️⃣ Iniciar proceso
        instance = process.initiate(process_id)
        case_id = instance.get("caseId")

        # 3️⃣ Obtener tareas del case
        activities = process.list_activities_by_case(case_id)

        print(f"Tareas pendientes en el case {case_id}:")
        for a in activities:
            print(f"- TaskId={a['id']} | Name={a['name']} | State={a['state']}")

        # 4️⃣ Guardar variable del proceso
        process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")

        # 5️⃣ Buscar tarea principal del proceso
        activities = process.search_activity_by_case(case_id)
        if not activities:
            return jsonify({"success": False, "error": "No hay tareas pendientes"})

        task_id = activities[0]["id"]

        # 6️⃣ Obtener usuario Bonita REAL
        bonita_user = process.get_user_by_name(bonita_username)

        # 7️⃣ Asignar tarea al usuario que está logueado
        assign_resp = process.assign_task(task_id, bonita_user["id"])
        print("assign_resp:", assign_resp)

        # 8️⃣ Completar tarea
        result = process.complete_activity(task_id)
        print("complete_activity:", result)

        return jsonify({
            "success": True,
            "result": {
                "caseId": case_id,
                "taskId": task_id,
                "completed_by": bonita_username,
                "complete": result
            }
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
