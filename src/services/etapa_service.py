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