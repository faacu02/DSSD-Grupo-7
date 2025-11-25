from models.etapa import Etapa
from db import db
from models.proyecto import Proyecto

def crear_etapa(nombre_etapa,
                    fecha_inicio,
                    fecha_fin,
                    tipo_cobertura,
                    cobertura_solicitada,
                    proyecto_id,
                    etapa_cloud_id):
    nuevo = Etapa(nombre=nombre_etapa, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
                  tipo_cobertura=tipo_cobertura, cobertura_solicitada=cobertura_solicitada,
                  proyecto_id=proyecto_id,
                  etapa_cloud_id=etapa_cloud_id)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_etapas():
    return Etapa.query.all()

def obtener_etapas_por_proyecto(proyecto_id):
    return Etapa.query.filter_by(proyecto_id=proyecto_id).all()

def obtener_etapa_por_id(etapa_id):
    return Etapa.query.get(etapa_id)

import json

def actualizar_cobertura(etapa_id, nueva_cobertura):
    etapa = obtener_etapa_por_id(etapa_id)
    if etapa:
        etapa.cobertura_actual = json.dumps(nueva_cobertura)
        db.session.commit()
        return etapa
    return None

def marcar_etapa_completa(etapa_id):
    etapa = obtener_etapa_por_id(etapa_id)
    if etapa:
        etapa.estado = 'Completa'
        db.session.commit()
        return etapa
    return None