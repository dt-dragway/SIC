"""
Script para crear las tablas del sistema de aprendizaje de IA.

Ejecutar:
    python3 create_learning_tables.py
"""

import sys
import os

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import engine
from app.infrastructure.database.learning_models import Base, AIProgress
from sqlalchemy.orm import Session

def create_tables():
    """Crear tablas de learning en la base de datos"""
    print("🔧 Creando tablas de AI Learning...")
    
    try:
        # Crear todas las tablas definidas en learning_models
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Tablas creadas exitosamente:")
        print("   - ai_analyses")
        print("   - prediction_results")
        print("   - ai_progress")
        
        # Inicializar AIProgress si no existe
        from app.infrastructure.database.session import SessionLocal
        db = SessionLocal()
        
        existing = db.query(AIProgress).first()
        if not existing:
            initial_progress = AIProgress(
                level=1,
                experience_points=0,
                total_analyses=0,
                correct_predictions=0,
                incorrect_predictions=0,
                pending_predictions=0,
                accuracy=0.0,
                tools_mastered=0
            )
            db.add(initial_progress)
            db.commit()
            print("✅ AIProgress inicializado: Nivel 1, 0 XP")
        else:
            print(f"ℹ️  AIProgress ya existe: Nivel {existing.level}, {existing.experience_points} XP")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        raise

if __name__ == "__main__":
    create_tables()
