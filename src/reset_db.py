from app import app, db
from models import etapa
from models import proyecto# importa todos tus modelos

with app.app_context():
    print("🔄 Eliminando todas las tablas...")
    db.drop_all()

    print("🧱 Creando tablas nuevamente según los modelos...")
    db.create_all()

    print("✅ Base de datos reseteada correctamente.")
