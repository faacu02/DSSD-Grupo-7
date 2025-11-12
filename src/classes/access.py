import requests

class AccessAPI:
    _session = None   # sesión compartida entre todas las llamadas
    _cookies = {}
    _user = None
    _password = None
    _base_url = None
    

    def __init__(self, base_url="http://localhost:8080/bonita/"):
        self.base_url = base_url
        self.login_url = f"{base_url}loginservice"

    def login(self, user="walter.bates", password="bpm"):
        s = requests.Session()
        resp = s.post(
            self.login_url,
            data={
                "username": user,
                "password": password,
                "redirect": "false"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
        )

        if resp.status_code not in [200, 204]:
            raise Exception(f"Error login Bonita: {resp.status_code} {resp.text}")

        AccessAPI._session = s
        AccessAPI._cookies = s.cookies.get_dict()
        AccessAPI._user = user
        AccessAPI._password = password
        AccessAPI._base_url = self.base_url

        print(f"✅ Login exitoso en Bonita como {user}")
        print("Cookies:", AccessAPI._cookies)
        return s

    @staticmethod
    def get_bonita_session():
        """Devuelve la sesión logueada globalmente, o reloguea si no existe"""
        if not AccessAPI._session:
            print("⚠️ No había sesión activa, realizando login automático...")
            api = AccessAPI(AccessAPI._base_url or "http://localhost:8080/bonita/")
            api.login(AccessAPI._user or "walter.bates", AccessAPI._password or "bpm")
        return AccessAPI._session