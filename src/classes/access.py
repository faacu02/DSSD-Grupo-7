import requests
from flask import session, Flask
from requests.cookies import RequestsCookieJar as SessionCookieJar
class AccessAPI:

   def login(self):
    user = "walter.bates"
    password = "bpm"
    BONITA_URL = "http://localhost:8080/bonita/"
    login_url = f"{BONITA_URL}loginservice"

    # Creamos una sesión HTTP para mantener cookies
    s = requests.Session()

    # Mandamos request de login
    resp = s.post(login_url, data={
        "username": user,
        "password": password,
        "redirect": "false"
    })

    if resp.status_code == 200:
        # Bonita devuelve la cookie X-Bonita-API-Token
        token = s.cookies.get("X-Bonita-API-Token")

        # Guardamos en la sesión de Flask
        session["bonita_user"] = user
        session["bonita_password"] = password
        session["bonita_base_url"] = BONITA_URL
        session["bonita_token"] = token
        session["logged"] = True

        return token,s
    else:
        raise Exception("No se pudo conectar al servidor de Bonita")
        

   