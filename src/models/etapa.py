from db import db

class Etapa(db.Model):
    __tablename__ = 'etapa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    tipo_cobertura = db.Column(db.String(50), nullable=False) 
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'), nullable=False)
    cobertura_solicitada = db.Column(db.String, nullable=False)
    cobertura_actual = db.Column(db.String, nullable=True)
    etapa_cloud_id = db.Column(db.Integer, nullable=True)