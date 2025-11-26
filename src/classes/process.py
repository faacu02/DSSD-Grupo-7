from wsgiref import headers
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
        self.base_group = f"{base_url}API/identity/group"
        self.base_membership = f"{base_url}API/identity/membership"
        self.base_role = f"{base_url}API/identity/role"
        self.base_actor = f"{base_url}API/bpm/actor"
        self.base_actor_member = f"{base_url}API/bpm/actorMember"
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

    
    def get_case_variable(self, case_id, varname):
        url = f"{self.base_case_variable}/{case_id}/{varname}"

        headers = {
            "Accept": "application/json",
            "X-Bonita-API-Token": self.token
        }

        r = self.session.get(url, headers=headers)

        if r.status_code == 404:
            return None  # variable aún no creada

        r.raise_for_status()
        return r.json().get("value")


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

    def get_user_groups(self, user_id):
        """
        Obtiene todos los grupos a los que pertenece un usuario.
        user_id: ID del usuario en Bonita
        Retorna: Lista de grupos con su información completa
        """
        url = f"{self.base_membership}?f=user_id={user_id}&p=0&c=100"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        memberships = r.json()
        
        # Obtener información completa de cada grupo
        groups = []
        for membership in memberships:
            group_id = membership.get("group_id")
            if group_id:
                group_info = self.get_group_by_id(group_id)
                if group_info:
                    groups.append(group_info)
        
        return groups

    def get_group_by_id(self, group_id):
        """
        Obtiene información de un grupo por su ID.
        group_id: ID del grupo en Bonita
        Retorna: Información del grupo (id, name, displayName, etc.)
        """
        url = f"{self.base_group}/{group_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_user_groups_names(self, user_id):
        """
        Obtiene solo los nombres de los grupos a los que pertenece un usuario.
        user_id: ID del usuario en Bonita
        Retorna: Lista de nombres de grupos
        """
        groups = self.get_user_groups(user_id)
        return [group.get("name") or group.get("displayName") for group in groups]

    def get_user_groups_paths(self, user_id):
        """
        Obtiene los paths completos de los grupos a los que pertenece un usuario.
        user_id: ID del usuario en Bonita
        Retorna: Lista de paths de grupos (ej: '/acme/Organizaciones/Interviniente')
        """
        groups = self.get_user_groups(user_id)
        paths = []
        for group in groups:
            path = group.get("path")
            name = group.get("name")
            # El path completo es path + "/" + name
            if path and name:
                full_path = f"{path}/{name}"
                paths.append(full_path)
            elif name:
                paths.append(f"/{name}")
        return paths

    def get_user_groups_display_names(self, user_id):
        """
        Obtiene el displayName de los grupos a los que pertenece un usuario.
        user_id: ID del usuario en Bonita
        Retorna: Lista de displayNames de grupos (ej: 'Interviniente', 'Services')
        """
        groups = self.get_user_groups(user_id)
        group_names = []
        for group in groups:
            # Usar displayName que tiene el nombre legible del grupo
            display_name = group.get("displayName")
            if display_name:
                group_names.append(display_name)
        
        return group_names

    def get_all_groups(self):
        """
        Obtiene todos los grupos disponibles en Bonita.
        Retorna: Lista de todos los grupos
        """
        url = f"{self.base_group}?p=0&c=100"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_user_roles(self, user_id):
        """
        Obtiene todos los roles del usuario a través de sus memberships.
        user_id: ID del usuario en Bonita
        Retorna: Lista de roles con su información completa
        """
        url = f"{self.base_membership}?f=user_id={user_id}&p=0&c=100"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        memberships = r.json()
        
        # Obtener información completa de cada rol
        roles = []
        role_ids_seen = set()  # Para evitar duplicados
        for membership in memberships:
            role_id = membership.get("role_id")
            if role_id and role_id not in role_ids_seen:
                role_ids_seen.add(role_id)
                role_info = self.get_role_by_id(role_id)
                if role_info:
                    roles.append(role_info)
        
        return roles

    def get_role_by_id(self, role_id):
        """
        Obtiene información de un rol por su ID.
        role_id: ID del rol en Bonita
        Retorna: Información del rol (id, name, displayName, etc.)
        """
        url = f"{self.base_role}/{role_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_user_roles_names(self, user_id):
        """
        Obtiene solo los nombres de los roles del usuario.
        user_id: ID del usuario en Bonita
        Retorna: Lista de nombres de roles (sin duplicados)
        """
        roles = self.get_user_roles(user_id)
        return [role.get("name") for role in roles if role.get("name")]

    def get_all_roles(self):
        """
        Obtiene todos los roles disponibles en Bonita.
        Retorna: Lista de todos los roles
        """
        url = f"{self.base_role}?p=0&c=100"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_user_actors(self, user_id, process_id=None):
        """
        Obtiene los actores (organizaciones) a los que pertenece un usuario.
        user_id: ID del usuario en Bonita
        process_id: (Opcional) ID del proceso para filtrar actores
        Retorna: Lista de actores con su información completa
        """
        # Obtener todos los actorMembers del usuario
        url = f"{self.base_actor_member}?f=user_id={user_id}&p=0&c=100"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        actor_members = r.json()
        
        # Obtener información completa de cada actor
        actors = []
        actor_ids_seen = set()  # Para evitar duplicados
        
        for member in actor_members:
            actor_id = member.get("actor_id")
            if actor_id and actor_id not in actor_ids_seen:
                actor_ids_seen.add(actor_id)
                actor_info = self.get_actor_by_id(actor_id)
                
                # Si se especificó process_id, filtrar por proceso
                if process_id:
                    if actor_info and str(actor_info.get("process_id")) == str(process_id):
                        actors.append(actor_info)
                else:
                    if actor_info:
                        actors.append(actor_info)
        
        return actors

    def get_actor_by_id(self, actor_id):
        """
        Obtiene información de un actor por su ID.
        actor_id: ID del actor en Bonita
        Retorna: Información del actor (id, name, displayName, process_id, etc.)
        """
        url = f"{self.base_actor}/{actor_id}"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def get_user_actors_names(self, user_id, process_id=None):
        """
        Obtiene solo los nombres de los actores/organizaciones del usuario.
        user_id: ID del usuario en Bonita
        process_id: (Opcional) ID del proceso para filtrar actores
        Retorna: Lista de nombres de actores/organizaciones
        """
        actors = self.get_user_actors(user_id, process_id)
        return [actor.get("displayName") or actor.get("name") for actor in actors if actor.get("displayName") or actor.get("name")]

    def get_all_actors(self, process_id=None):
        """
        Obtiene todos los actores disponibles en Bonita.
        process_id: (Opcional) ID del proceso para filtrar actores
        Retorna: Lista de todos los actores
        """
        url = f"{self.base_actor}?p=0&c=100"
        if process_id:
            url = f"{self.base_actor}?f=process_id={process_id}&p=0&c=100"
        r = self.session.get(url, headers=self._headers(with_json=False))
        r.raise_for_status()
        return r.json()

    def wait_for_case_variable(self, case_id, varname, timeout=10, interval=0.3):
        """
        Espera hasta que una variable de case exista y NO sea null.
        """
        import time
        start = time.time()

        while time.time() - start < timeout:
            value = self.get_case_variable(case_id, varname)
            print(f"[DEBUG] polling {varname}:", value)

            if value not in (None, "null", ""):
                return value

            time.sleep(interval)

        print(f"[WARN] timeout esperando {varname} en case {case_id}")
        return None
    
    def get_cases_by_process_id(self, process_id):
        """
        Devuelve los casos de un proceso, ordenados por fecha de inicio DESC.
        Compatible con Bonita 7.x
        """
        url = f"{self.base_url}API/bpm/case"
        params = {
            "f": f"processDefinitionId={process_id}",
            "o": "startDate DESC",
            "p": 0,
            "c": 10
        }

        headers = {
            "X-Bonita-API-Token": self.session.cookies.get("X-Bonita-API-Token", "")
        }

        resp = self.session.get(url, params=params, headers=headers)

        if resp.status_code != 200:
            raise Exception(f"Error al obtener casos del proceso: {resp.text}")

        print("Respuesta Bonita:", resp.text)  # debugging

        return resp.json()


    
    
 