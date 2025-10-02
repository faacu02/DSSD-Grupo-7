from models.proyecto import Proyecto
from db import db

def crear_proyecto(nombre):
    nuevo = Proyecto(nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_proyectos():
    return Proyecto.query.all()