from db import db

class Proyecto(db.Model):
    __tablename__ = 'proyecto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    case_id = db.Column(db.Integer, nullable=True)
    case_id_obs = db.Column(db.Integer, nullable=True)