# 🔐 Credenciales de Acceso - SIC Ultra

## Usuario Administrador

**Email:** `admin@sic.com`  
**Password:** `Admin123!`  
**Nombre:** Administrador

---

## Acceso al Frontend

1. **URL:** http://localhost:3000 (o el puerto donde corre Next.js)
2. **Email:** admin@sic.com
3. **Password:** Admin123!
4. **Click:** Login

---

## Crear Más Usuarios

### Vía API:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "name": "Nombre Usuario",
    "password": "Password123!"
  }'
```

### Vía Frontend:
1. Ir a página de registro
2. Completar formulario
3. Click en "Registrarse"

---

## Recuperar Password

Si olvidas el password, puedes resetearlo directamente en la BD:

```bash
psql -U sic_user -d sic_db -h localhost -c "
UPDATE users 
SET password = '\$2b\$12\$HASH_AQUI' 
WHERE email = 'admin@sic.com';
"
```

---

## IMPORTANTE ⚠️

**Cambiar password después del primer login:**
1. Login con credenciales por defecto
2. Ir a Configuración / Perfil
3. Cambiar password a uno seguro

---

**Credenciales actuales:**
- Email: `admin@sic.com`
- Password: `Admin123!`
