from flask import Blueprint, request, jsonify
from classes.process import Process
from classes.access import AccessAPI

bonita_bp = Blueprint("bonita", __name__, url_prefix="/bonita")

@bonita_bp.route("/completar_actividad", methods=["POST"])
def completar_actividad():
    nombre = request.json.get("nombre")

    try:
        # Usar la sesión existente en lugar de hacer login nuevamente
        session = AccessAPI.get_bonita_session()
        process = Process(session)

        process_id = process.get_process_id_by_name("Proceso de generar proyecto")
        instance = process.initiate(process_id)
        case_id = instance.get("caseId")
        activities = process.list_activities_by_case(case_id)

        print(f"Tareas pendientes en el case {case_id}:")
        for a in activities:
            print(f"- TaskId={a['id']} | Name={a['name']} | State={a['state']} | Assigned={a['assigned_id']}")

        process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")

        activities = process.search_activity_by_case(case_id)

        if not activities:
            return jsonify({"success": False, "error": "No hay tareas pendientes"})
        task_id = activities[0]["id"]

        
        user = process.get_user_by_name("walter.bates")

        assign_resp = process.assign_task(task_id, user["id"])
        print("assign_resp parsed:", assign_resp)

        task = session.get(f"http://localhost:8080/bonita/API/bpm/userTask/{task_id}",
                    headers=process._headers(with_json=False)).json()
        print("task after assign:", task)
       
       

        result = process.complete_activity(task_id)
        print("complete_activity parsed:", result)

        state = process.check_task_state(task_id)
        print("state after complete:", state)

        activities = process.list_activities_by_case(case_id)

        print(f"Tareas pendientes en el case {case_id}:")
        #for a in activities:
        #    print(f"- TaskId={a['id']} | Name={a['name']} | State={a['state']} | Assigned={a['assigned_id']}")

        return jsonify({
            "success": True,
            "result": {
                "caseId": case_id,
                "taskId": task_id,
                "complete": result
            }
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})