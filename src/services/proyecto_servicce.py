from models.proyecto import Proyecto
from db import db

def crear_proyecto(nombre, cantidad_etapas):
    nuevo = Proyecto(nombre=nombre, cantidad_etapas=cantidad_etapas)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_proyectos():
    return Proyecto.query.all()