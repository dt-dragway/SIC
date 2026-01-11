import sqlite3
from datetime import datetime
import uuid
import logging

class DBManager:
    def __init__(self, db_path='database/sic.db'):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def log_alert(self, alert_type, message):
        """
        Registra una alerta en la BD con un ID único (Solución al bug UNIQUE constraint)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Generamos un UUID único para evitar el error de restricción UNIQUE
            alert_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            cursor.execute(
                "INSERT INTO alerts (id, type, message, timestamp) VALUES (?, ?, ?, ?)",
                (alert_id, alert_type, message, timestamp)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error insertando alerta en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_transactions(self):
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Usamos la tabla 'transacciones' que coincide con las columnas del HTML (tipo, cantidad, precio, fecha)
            cursor.execute("SELECT * FROM transacciones ORDER BY fecha DESC LIMIT 50")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error leyendo transacciones: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_transaction(self, tipo, cantidad, precio):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                "INSERT INTO transacciones (tipo, cantidad, precio, fecha) VALUES (?, ?, ?, ?)",
                (tipo, cantidad, precio, fecha)
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error guardando transacción: {e}")
            return False
        finally:
            if conn:
                conn.close()
