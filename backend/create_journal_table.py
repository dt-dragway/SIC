import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.session import engine
from app.infrastructure.database.models import JournalEntry

def create_table():
    print("Creando tabla journal_entries...")
    JournalEntry.__table__.create(bind=engine, checkfirst=True)
    print("Tabla creada.")

if __name__ == "__main__":
    create_table()
