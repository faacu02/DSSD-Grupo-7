from flask import Blueprint, request, jsonify
from classes.process import Process
from classes.access import AccessAPI

bonita_bp = Blueprint("bonita", __name__, url_prefix="/bonita")

@bonita_bp.route("/completar_actividad", methods=["POST"])
def completar_actividad():
    access = AccessAPI()
    nombre = request.json.get("nombre")
    cantidad_etapas = request.json.get("cantidad_etapas")

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
        process.set_variable_by_case(case_id, "nombre_proyecto", nombre, "java.lang.String")
        process.set_variable_by_case(case_id, "cantidad_etapas", cantidad_etapas, "java.lang.Integer")

        # Solo devolver el case_id, no buscar ni completar tareas
        return jsonify({"success": True, "result": {"caseId": case_id}})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})