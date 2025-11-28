import requests

class AccessAPI:
    def __init__(self, base_url="http://localhost:8080/bonita/"):
        self.base_url = base_url
        self.login_url = f"{base_url}loginservice"

    def login(self, user, password):
        """
        Realiza login en Bonita y devuelve una requests.Session()
        con las cookies ya cargadas.
        """
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
            raise Exception(f"Credenciales incorrectas")

        print(f"✅ Login exitoso en Bonita como {user}")
        print("Cookies:", s.cookies.get_dict())

        return s   # ← devolvemos la sesión REAL

    @staticmethod
    def build_session_from_cookies(cookies: dict):
        """
        Reconstruye una requests.Session() a partir de las cookies
        guardadas en la sesión Flask.
        """
        s = requests.Session()
        s.cookies.update(cookies)
        return s
