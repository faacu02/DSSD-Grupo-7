import requests

class Process:

    def __init__(self):
        self.session = requests.Session()
        self.base = "http://localhost:8080/bonita/API/bpm/process"
        
    def get_all_process(self):
        """
        Lista todos los procesos disponibles en Bonita.
        Equivalente a GET /API/bpm/process?p=0&c=1000
        Devuelve un array de procesos con id, name, version, etc.
        """
        r = self.session.get(f"{self.base}?p=0&c=1000")
        return r.json()
    
    def get_process_name(self, process_id):

        """
        Obtiene el nombre de un proceso a partir de su ID.
        GET /API/bpm/process/{process_id}
        """
        r = self.session.get(f"{self.base}/{process_id}")
        return r.json()
    
    def get_process_id_by_name(self, process_name):
        url = f"{self.base}?f=name={process_name}&p=0&c=10&f=activationState=ENABLED"
        r = self.session.get(url)
        data = r.json()
        if data:
            return data[0].get("id")
        return None
    
    def get_count_process(self):

        """
        Cuenta cuántos procesos hay desplegados en Bonita.
        Lo hace pidiendo hasta 1000 procesos y devolviendo la cantidad.
        """

        r = self.session.get(f"{self.base}?p=0&c=1000")
        return len(r.json())
    


    def initiate(self, process_id):
        """
        Inicia una nueva instancia de un proceso por ID.
        POST /API/bpm/process/{process_id}/instantiation
        Devuelve datos de la nueva instancia (caseId, etc.).
        """
        r = self.session.post(f"{self.base}/{process_id}/instantiation")
        return r.json()
    


    def set_variable_by_case(self, case_id, variable, value, tipo="java.lang.String"):
        """
        Cambia el valor de una variable en una instancia (case).
        PUT /API/bpm/caseVariable/{case_id}/{variable}
        tipo: por defecto 'java.lang.String' (también puede ser Integer, Boolean, etc.).
        """
        url = f"http://localhost:8080/bonita/API/bpm/caseVariable/{case_id}/{variable}"
        r = self.session.put(url, json={"value": value, "type": tipo})
        return r.json()
    
    def set_variable_from_task(self, task_id, variable, value, tipo="java.lang.String"):
        """
        Versión vieja: usa taskId para obtener caseId y luego setear variable.
        1. GET /API/bpm/userTask/{taskId} -> obtener caseId
        2. PUT /API/bpm/caseVariable/{caseId}/{variable}
        """
        task = self.session.get(f"http://localhost:8080/bonita/API/bpm/userTask/{task_id}").json()
        case_id = task.get("caseId")
        url = f"http://localhost:8080/bonita/API/bpm/caseVariable/{case_id}/{variable}"
        payload = {"value": value, "type": tipo}
        r = self.session.put(url, json=payload)
        return r.json()

    def assign_task(self, task_id, user_id):
        """
        Asigna una tarea de usuario a un usuario específico.
        PUT /API/bpm/userTask/{taskId}
        Body: { "assigned_id": userId }
        """
        url = f"{self.base_task}/{task_id}"
        r = self.session.put(url, json={"assigned_id": user_id})
        return r.json()
    

    def search_activity_by_case(self, case_id):
        """
        Busca todas las actividades (tareas) asociadas a un caso.
        GET /API/bpm/task?f=caseId={caseId}
        """
        url = f"http://localhost:8080/bonita/API/bpm/task?f=caseId={case_id}"
        r = self.session.get(url)
        return r.json()

    def complete_activity(self, task_id):
        """
        Completa (ejecuta) una tarea de usuario.
        POST /API/bpm/userTask/{taskId}/execution
        """
        url = f"{self.base_task}/{task_id}/execution"
        r = self.session.post(url)
        return r.json()
    


    def get_variable(self, task_id, variable):
        """
        Obtiene el valor de una variable a partir de una tarea.
        1. Busca la tarea para obtener caseId
        2. Hace GET /API/bpm/caseVariable/{caseId}/{variable}
        """
        task_url = f"{self.base_task}/{task_id}"
        case_data = self.session.get(task_url).json()
        case_id = case_data.get("caseId")
        url = f"{self.base_case_variable}/{case_id}/{variable}"
        r = self.session.get(url)
        return r.json()
    
    def get_variable_by_case(self, case_id, variable):
        """
        Obtiene el valor de una variable directamente con caseId.
        GET /API/bpm/caseVariable/{caseId}/{variable}
        """
        url = f"{self.base_case_variable}/{case_id}/{variable}"
        r = self.session.get(url)
        return r.json()
