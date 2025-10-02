import requests

class Process:
    def __init__(self, session, base_url="http://localhost:8080/bonita/"):
        self.session = session
        self.base_url = base_url
        self.base_process = f"{base_url}API/bpm/process"
        self.base_task = f"{base_url}API/bpm/userTask"
        self.base_case_variable = f"{base_url}API/bpm/caseVariable"
        self.base_user = f"{base_url}API/identity/user"
        self.base_task_list = f"{base_url}API/bpm/task"
        # Token de Bonita
        self.token = session.cookies.get("X-Bonita-API-Token")

    def _headers(self, with_json=True):
        headers = {
            "Accept": "application/json",
            "X-Bonita-API-Token": self.token
        }
        if with_json:
            headers["Content-Type"] = "application/json"
        return headers

    def _safe_json(self, r):
        """Devuelve JSON si hay contenido, sino un dict simple."""
        if r.status_code == 204 or not r.text.strip():
            return {"status": "ok"}
        return r.json()

    def get_user_by_name(self, user_name):
        url = f"{self.base_user}?f=userName={user_name}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()[0] if r.json() else None

    def get_all_process(self):
        url = f"{self.base_process}?p=0&c=1000"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_process_name(self, process_id):
        url = f"{self.base_process}/{process_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_process_id_by_name(self, process_name):
        url = f"{self.base_process}?f=name={process_name}&p=0&c=10&f=activationState=ENABLED"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        data = r.json()
        return data[0]["id"] if data else None

    def get_count_process(self):
        url = f"{self.base_process}?p=0&c=1000"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return len(r.json())

    def initiate(self, process_id):
        url = f"{self.base_process}/{process_id}/instantiation"
        r = self.session.post(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return self._safe_json(r)

    def set_variable_by_case(self, case_id, variable, value, tipo="java.lang.String"):
        url = f"{self.base_case_variable}/{case_id}/{variable}"
        payload = {"value": value, "type": tipo}
        r = self.session.put(url, json=payload, headers=self._headers())
        r.raise_for_status()
        return self._safe_json(r)

    def set_variable_from_task(self, task_id, variable, value, tipo="java.lang.String"):
        task = self.session.get(f"{self.base_task}/{task_id}", headers=self._headers(with_json=False)).json()
        case_id = task.get("caseId")
        url = f"{self.base_case_variable}/{case_id}/{variable}"
        payload = {"value": value, "type": tipo}
        r = self.session.put(url, json=payload, headers=self._headers())
        r.raise_for_status()
        return self._safe_json(r)

    def assign_task(self, task_id, user_id):
        url = f"{self.base_task}/{task_id}"
        payload = {"assigned_id": str(user_id)}  # forzar string

        print("\n[DEBUG] Assign task")
        print("  URL:", url)
        print("  Payload:", payload)
        print("  Headers:", self._headers())

        r = self.session.put(url, json=payload, headers=self._headers())

        print("  Status:", r.status_code)
        print("  Response text:", r.text)

        try:
            r.raise_for_status()
        except Exception as e:
            print("  ERROR in assign_task:", e)
            raise

        return self._safe_json(r)



    def get_actors_by_process(self, process_id):
        url = f"{self.base_url}API/bpm/actor?f=process_id={process_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def search_activity_by_case(self, case_id):
        url = f"{self.base_task_list}?f=caseId={case_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def complete_activity(self, task_id, contract=None):
       
        url = f"{self.base_task}/{task_id}/execution"
        payload = {"contract": contract} if contract else {}

        print("\n[DEBUG] Complete activity")
        print("  URL:", url)
        print("  Payload:", payload)
        print("  Headers:", self._headers())

        r = self.session.post(url, json=payload, headers=self._headers())

        print("  Status:", r.status_code)
        print("  Response text:", r.text)

        # Manejo de 204 (sin contenido)
        if r.status_code == 204 or not r.text.strip():
            return {"status": "completed"}

        r.raise_for_status()
        return self._safe_json(r)


    def get_variable(self, task_id, variable):
        task_url = f"{self.base_task}/{task_id}"
        case_data = self.session.get(task_url, headers=self._headers(with_json=False)).json()
        case_id = case_data.get("caseId")
        url = f"{self.base_case_variable}/{case_id}/{variable}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_variable_by_case(self, case_id, variable):
        url = f"{self.base_case_variable}/{case_id}/{variable}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_actor_members(self, actor_id):
        """
        Devuelve los miembros (usuarios, grupos, roles) asociados a un actor.
        actor_id: id del actor (string o int).
        """
        url = f"{self.base_url}API/bpm/actorMember?f=actor_id={actor_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()


    def check_task_state(self, task_id):
        url = f"{self.base_task}/{task_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        if r.status_code == 404:
            return {"state": "not_found"}
        if r.status_code == 204 or not r.text.strip():
            return {"state": "completed"}
        data = r.json()
        return {"state": data.get("state", "unknown")}
    
    
    def list_activities_by_case(self, case_id):
        """
        Devuelve todas las actividades pendientes de un case.
        """
        url = f"{self.base_task_list}?f=caseId={case_id}&c=50"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()