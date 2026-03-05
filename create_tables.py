import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app.infrastructure.database.session import engine
from app.infrastructure.database.models import Base, JournalEntry

def create_tables():
    print("Creando tablas...")
    JournalEntry.__table__.create(bind=engine, checkfirst=True)
    print("Tablas creadas.")

if __name__ == "__main__":
    create_tables()
