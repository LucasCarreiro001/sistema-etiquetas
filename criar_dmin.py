from database import SessionLocal
from models import Usuarios
from auth import hash_password

db = SessionLocal()

admin = Usuarios(
    nome="Lucas Carreiro",
    email="lucas@admin.com",
    senha_hash=hash_password("lucas123456"),
    cargo="admin"
)

db.add(admin)
db.commit()
db.refresh(admin)

print(f"Admin criado com sucesso! id: {admin.id}, email: {admin.email}")

db.close()