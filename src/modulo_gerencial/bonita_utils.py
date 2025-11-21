# services/bonita_utils.py
import requests
from flask import  session


def get_bonita_session() -> requests.Session:
    """
    Devuelve una sesión autenticada hacia Bonita.
    Si no hay cookies en Flask, intenta loguear automáticamente.
    """
    cookies = session.get("bonita_cookies")

    # Si no hay cookies → intentamos autologin
    if not cookies:
        username = "walter.bates"
        password = "bpm"  # Cambiá esto por la contraseña real

      

        # Hacemos login nuevamente
        from classes.access import AccessAPI  
        bonita_session = AccessAPI().login(username, password)

        # Guardamos cookies nuevas
        cookies = bonita_session.cookies.get_dict()
        session["bonita_cookies"] = cookies

    # Construimos la sesión
    s = requests.Session()
    s.cookies.update(cookies)

    token = cookies.get("X-Bonita-API-Token")
    headers = {"Accept": "application/json"}
    if token:
        headers["X-Bonita-API-Token"] = token

    s.headers.update(headers)
    return s



def get_process_id_by_name(process_name: str) -> int:
    """
    Busca un proceso por nombre en Bonita y devuelve su ID.
    """
    s = get_bonita_session()
    base = "http://localhost:8080/bonita"

    url = f"{base}/API/bpm/process"
    params = {
        "f": [f"name={process_name}"],
        "c": "100"
    }

    resp = s.get(url, params=params)
    resp.raise_for_status()
    processes = resp.json()

    if not processes:
        raise RuntimeError(f"No se encontró el proceso llamado: {process_name}")

    return int(processes[0]["id"])


def obtener_casos_completados(process_id: int) -> list[dict]:
    """
    Devuelve todos los casos completados (archivedCase) de un proceso.
    """
    s = get_bonita_session()
    base = "http://localhost:8080/bonita"

    url = f"{base}/API/bpm/archivedCase"
    resp = s.get(url, params={
        "f": [f"processDefinitionId={process_id}"],
        "c": "9999"
    })
    resp.raise_for_status()
    return resp.json()

import requests

def get_archived_tasks(case_id: int, task_name: str = None):
    """
    Devuelve las tareas archivadas (completadas) de un caso de Bonita.
    Si pasás task_name, filtra por nombre exacto de la tarea.
    """

    # Obtener sesión autenticada a Bonita
    session = get_bonita_session()

    base_url = "http://localhost:8080/bonita"

    # Armamos filtros
    params = {
        "f": [f"caseId={case_id}"],
        "o": "archivedDate ASC",  # ordenadas por fecha
        "p": 0,
        "c": 1000                 # máximo de tareas a devolver
    }

    url = f"{base_url}/API/bpm/archivedUserTask"

    try:
        resp = session.get(url, params=params)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] No se pudieron obtener tareas archivadas: {e}")
        return []

    tareas = resp.json()

    # Si se quiere filtrar por nombre exacto
    if task_name:
        tareas = [t for t in tareas if t.get("displayName") == task_name or t.get("name") == task_name]

    return tareas

