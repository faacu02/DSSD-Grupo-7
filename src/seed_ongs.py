from db import db
from models.ong import ONG

def seed_ongs():
    # 1) borrar todas las ONGs existentes
    ONG.query.delete()

    # 2) crear las ONGs nuevas con los IDs de Bonita
    nuevas_ongs = [
        ONG(bonita_user_id=206, nombre="UNICEF"),     # ejemplo, reemplazar IDs
        ONG(bonita_user_id=201, nombre="Greenpeace"),
        ONG(bonita_user_id=207, nombre="Médicos Sin Fronteras"),
    ]

    # 3) guardar en la BD
    for o in nuevas_ongs:
        db.session.add(o)

    db.session.commit()
    print("✔ ONGs reinicializadas correctamente")
