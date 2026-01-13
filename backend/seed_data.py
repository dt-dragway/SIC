"""
Script para poblar la base de datos con un usuario inicial.
Uso: python3 seed_data.py
"""
import sys
import os
from datetime import datetime

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import engine, SessionLocal
from app.infrastructure.database.models import User
from app.api.v1.auth import hash_password

def seed_users():
    db = SessionLocal()
    try:
        # Verificar si ya existe admin
        existing_admin = db.query(User).filter(User.email == "admin@sic.com").first()
        if existing_admin:
            print("⚠️  El usuario 'admin@sic.com' ya existe.")
            return

        # Crear usuario Admin con password aleatorio SEGURO
        import secrets
        admin_password = os.getenv("ADMIN_PASSWORD", secrets.token_urlsafe(16))
        
        print("👤 Creando usuario administrador...")
        admin_user = User(
            email="admin@sic.com",
            name="Administrador SIC",
            password_hash=hash_password(admin_password),
            has_2fa=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Usuario creado exitosamente:")
        print("   Email: admin@sic.com")
        print(f"   Password: {admin_password}")
        print("\n⚠️  GUARDA ESTA PASSWORD EN UN LUGAR SEGURO")
        print("⚠️  Esta es la única vez que se mostrará\n")
        
    except Exception as e:
        print(f"❌ Error al crear datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
