from flask import Blueprint, Flask, session, jsonify, request
import requests

bp = Blueprint("jya", __name__)

def do_request(method, uri, variable=None, data=None, type=None, assign_task=False):
    response = {}
    try:
        headers = {
            "X-Bonita-API-Token": session.get("X-Bonita-API-Token")
        }

        if method == "POST":
            r = requests.post(uri, headers=headers)
            response["success"] = True
            response["data"] = r.json()

        elif method == "PUT":
            if assign_task:
                payload = {
                    "assigned_id": data
                }
            else:
                payload = {
                    "type": f"java.lang.{type}",
                    "value": data
                }

            r = requests.put(uri, headers=headers, json=payload)
            response["success"] = True
            response["data"] = r.json()

        else:
            response["success"] = False
            response["error"] = f"Método {method} no soportado"

    except Exception as e:
        response["success"] = False
        response["error"] = str(e)

    return response

@bp.route("/<path:uri>", methods=["POST", "PUT"])
def bonita_proxy(uri):
    method = request.method
    data = request.json.get("data") if request.is_json else None
    type_ = request.json.get("type") if request.is_json else None
    assign_task = request.args.get("assign_task", "false").lower() == "true"

    # Construyo la URL completa a Bonita (ajústalo a tu servidor Bonita)
    bonita_url = f"http://localhost:8080/bonita/API/{uri}"

    result = do_request(method, bonita_url, data=data, type=type_, assign_task=assign_task)
    return jsonify(result)