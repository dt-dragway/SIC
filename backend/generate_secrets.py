#!/usr/bin/env python3
"""
Generador de Secretos Seguros para SIC Ultra

Ejecuta este script para generar claves criptográficamente seguras.
"""

import secrets

def generate_secret(length=64):
    """Genera un secret aleatorio seguro"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("🔐 Generando secretos seguros...\n")
    
    print("# Copia estas líneas a tu archivo .env")
    print("# NUNCA compartas estos valores\n")
    
    print(f"SECRET_KEY={generate_secret(64)}")
    print(f"JWT_SECRET_KEY={generate_secret(64)}")
    print(f"\n# Contraseña para admin (guárdala en lugar seguro)")
    print(f"ADMIN_PASSWORD={generate_secret(16)}")
    
    print("\n✅ Secretos generados exitosamente")
    print("⚠️  IMPORTANTE: Guarda estos valores de forma segura")
