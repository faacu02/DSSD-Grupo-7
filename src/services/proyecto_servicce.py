from models.proyecto import Proyecto
from db import db
from services.etapa_service import obtener_etapas_por_proyecto, obtener_etapa_por_id

def crear_proyecto(nombre):
    nuevo = Proyecto(nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_proyectos():
    return Proyecto.query.filter_by(completado=False).all()


def marcar_proyecto_como_completado(proyecto_id):
    proyecto = Proyecto.query.get(proyecto_id)
    etapas= obtener_etapas_por_proyecto(proyecto_id)
    if proyecto:
        for etapa in etapas:
            if etapa.estado != 'Completa':
                raise Exception("No se puede completar el proyecto, hay etapas incompletas")
        proyecto.completado = True
        db.session.commit()
        return proyecto
    else:
        raise ValueError("Proyecto no encontrado")
    
def obtener_proyecto_por_id(proyecto_id):
    return Proyecto.query.get(proyecto_id)

def obtener_proyectos_completados():
    return Proyecto.query.filter_by(completado=True).all()

def actualizar_case_id(proyecto_id, case_id):
    proyecto = Proyecto.query.get(proyecto_id)
    if proyecto:
        proyecto.case_id = case_id
        db.session.commit()
        return proyecto
    else:
        raise ValueError("Proyecto no encontrado")
    
    
def devolver_case_id_por_proyecto_id():
    ultimo = Proyecto.query.order_by(Proyecto.id.desc()).first()
    return ultimo.case_id

def hay_proyectos():
    return Proyecto.query.count() > 0

def set_case_id_obs(case_id, proyecto_id):
    proyecto = Proyecto.query.get(proyecto_id)
    if proyecto:
        proyecto.case_id_obs = case_id
        db.session.commit()
        return proyecto
    else:
        raise ValueError("Proyecto no encontrado")