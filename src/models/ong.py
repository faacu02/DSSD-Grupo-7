from db import db

class ONG(db.Model):
    __tablename__ = "ong"

    id = db.Column(db.Integer, primary_key=True)
    bonita_user_id = db.Column(db.Integer, nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<ONG {self.nombre}>"
