from models.proyecto import Proyecto
from db import db

def crear_proyecto(nombre):
    nuevo = Proyecto(nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_proyectos():
    return Proyecto.query.all()


def marcar_proyecto_como_completado(proyecto_id):
    proyecto = Proyecto.query.get(proyecto_id)
    if proyecto:
        proyecto.completado = True
        db.session.commit()
        return proyecto
    else:
        raise ValueError("Proyecto no encontrado")
    
def obtener_proyecto_por_id(proyecto_id):
    return Proyecto.query.get(proyecto_id)