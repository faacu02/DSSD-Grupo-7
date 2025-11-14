import requests

class AccessAPI:

    def __init__(self, base_url="http://localhost:8080/bonita/"):
        self.base_url = base_url
        self.login_url = f"{base_url}loginservice"

    def login(self, username, password):
        """Realiza login en Bonita y devuelve SOLO las cookies."""
        s = requests.Session()

        resp = s.post(
            self.login_url,
            data={
                "username": username,
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

        print(f"🔐 Login exitoso en Bonita como {username}")
        cookies = s.cookies.get_dict()
        print(f"Cookies Bonita ({username}): {cookies}")

        return cookies  # ⬅ ESTA ES LA PARTE IMPORTANTE
