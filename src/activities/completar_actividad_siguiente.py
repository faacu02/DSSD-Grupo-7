from flask import Blueprint, request, jsonify
from classes.process import Process
from classes.access import AccessAPI

bonita_bp_siguiente = Blueprint("bonita_siguiente", __name__, url_prefix="/bonita")

@bonita_bp_siguiente.route("/completar_actividad_siguiente", methods=["POST"])
def completar_actividad_siguiente():
    access = AccessAPI()
    # Recibe el case_id y los datos necesarios para la tarea
    case_id = request.json.get("case_id")
    nombre = request.json.get("nombre")  # Si necesitas setear variables

    try:
        # 1. Login
        cookie, session = access.login()

        # 2. Instanciar Process con la sesión autenticada
        process = Process(session)

        # 3. (Opcional) Setear variables si corresponde
        if nombre:
            set_var_resp = process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")
            print(f"set_variable_by_case response: {set_var_resp}")

        # 4. Buscar actividad pendiente en el case
        activities = process.search_activity_by_case(case_id)
        print(f"search_activity_by_case response: {activities}")
        if not activities:
            return jsonify({"success": False, "error": "No se encontraron actividades para el case."})
        task_id = activities[0].get("id")

        # 5. Buscar usuario genérico
        user = process.get_user_by_name("walter.bates")
        print(f"get_user_by_name response: {user}")

        # 6. Asignar tarea
        assign_resp = process.assign_task(task_id, user["id"])
        print(f"assign_task response: {assign_resp}")

        # 7. Completar actividad
        result = process.complete_activity(task_id)
        print(f"complete_activity response: {result}")

        return jsonify({"success": True, "result": result})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})
