from models.etapa import Etapa
from db import db
from models.proyecto import Proyecto

def crear_etapa(nombre_etapa,
                    fecha_inicio,
                    fecha_fin,
                    tipo_cobertura,
                    cobertura_solicitada,
                    proyecto_id):
    nuevo = Etapa(nombre=nombre_etapa, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
                  tipo_cobertura=tipo_cobertura, cobertura_solicitada=cobertura_solicitada,
                  proyecto_id=proyecto_id)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_etapas():
    return Etapa.query.all()

def obtener_etapas_por_proyecto(proyecto_id):
    return Etapa.query.filter_by(proyecto_id=proyecto_id).all()

def obtener_etapa_por_id(etapa_id):
    return Etapa.query.get(etapa_id)