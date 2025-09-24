import requests
from flask import session as flask_session

class AccessAPI:
    def __init__(self, base_url="http://localhost:8080/bonita/"):
        self.base_url = base_url
        self.login_url = f"{base_url}loginservice"
        self.user = "walter.bates"
        self.password = "bpm"

    def login(self):
        s = requests.Session()

        resp = s.post(
            self.login_url,
            data={
                "username": self.user,
                "password": self.password,
                "redirect": "false"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
        )

        print("status:", resp.status_code)
        print("cookies:", s.cookies.get_dict())

        if resp.status_code in [200, 204]:
            token = s.cookies.get("X-Bonita-API-Token")
            if not token:
                raise Exception("Login exitoso pero no se obtuvo token")

            # opcional: guardar en sesión de Flask
            flask_session["bonita_user"] = self.user
            flask_session["bonita_password"] = self.password
            flask_session["bonita_base_url"] = self.base_url
            flask_session["bonita_token"] = token
            flask_session["logged"] = True

            return token, s
        else:
            raise Exception(f"Error login Bonita: {resp.status_code} {resp.text}")
