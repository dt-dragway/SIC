"""
SIC Ultra - Sistema de Autenticación

Login con JWT, refresh tokens, 2FA opcional.
- Remember me: sesión de 30 días
- Dispositivo confiable: 2FA solo cada 30 días
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import secrets
from typing import Optional

from app.config import settings


router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# === Schemas ===

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    totp_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    has_2fa: bool
    created_at: datetime


# === Utility Functions ===

def hash_password(password: str) -> str:
    """Hash de contraseña con bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict, remember_me: bool = False) -> str:
    """
    Crear refresh token.
    Si remember_me es True, dura 30 días.
    """
    to_encode = data.copy()
    days = settings.remember_me_expire_days if remember_me else settings.refresh_token_expire_days
    expire = datetime.utcnow() + timedelta(days=days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_trusted_device_token(user_id: int) -> str:
    """
    Crear token de dispositivo confiable.
    Válido por 30 días - no pide 2FA durante este tiempo.
    """
    expire = datetime.utcnow() + timedelta(days=settings.trusted_device_expire_days)
    data = {
        "user_id": user_id,
        "exp": expire,
        "type": "trusted_device",
        "device_id": secrets.token_hex(16)
    }
    return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[dict]:
    """Verificar y decodificar token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def generate_totp_secret() -> str:
    """Generar secreto para 2FA"""
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    """Verificar código TOTP (Google Authenticator)"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


# === Endpoints ===

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Registrar nuevo usuario.
    
    - Email único
    - Password hasheado con bcrypt
    """
    # TODO: Verificar email único en DB
    # TODO: Guardar usuario en DB
    
    # Placeholder response
    return {
        "id": 1,
        "email": user.email,
        "name": user.name,
        "has_2fa": False,
        "created_at": datetime.utcnow()
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login de usuario.
    
    - Verifica credenciales
    - Si tiene 2FA, verifica código TOTP
    - Opción "recordarme" para sesión de 30 días
    - Cookie de dispositivo confiable para no pedir 2FA
    """
    # TODO: Buscar usuario en DB
    # TODO: Verificar password
    # TODO: Verificar 2FA si está habilitado
    
    # Verificar si tiene cookie de dispositivo confiable
    trusted_device_cookie = request.cookies.get("trusted_device")
    need_2fa = False  # TODO: Verificar si necesita 2FA
    
    if trusted_device_cookie:
        # Verificar token de dispositivo
        device_data = verify_token(trusted_device_cookie)
        if device_data and device_data.get("type") == "trusted_device":
            need_2fa = False  # No pedir 2FA, dispositivo confiable
    
    # Crear tokens
    user_data = {"sub": form_data.username, "user_id": 1}
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data, remember_me=True)  # TODO: Leer remember_me del form
    
    # Establecer cookie de dispositivo confiable (30 días)
    trusted_token = create_trusted_device_token(user_id=1)
    response.set_cookie(
        key="trusted_device",
        value=trusted_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.trusted_device_expire_days  # 30 días
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Renovar access token usando refresh token.
    """
    payload = verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    # Crear nuevo access token
    user_data = {"sub": payload["sub"], "user_id": payload.get("user_id")}
    new_access = create_access_token(user_data)
    
    return {
        "access_token": new_access,
        "refresh_token": refresh_token,  # Mismo refresh token
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/logout")
async def logout(response: Response):
    """
    Cerrar sesión.
    Elimina cookies de sesión.
    """
    response.delete_cookie("trusted_device")
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Obtener información del usuario actual.
    """
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # TODO: Buscar usuario en DB
    return {
        "id": payload.get("user_id", 1),
        "email": payload.get("sub"),
        "name": "Usuario",
        "has_2fa": False,
        "created_at": datetime.utcnow()
    }


@router.post("/2fa/enable")
async def enable_2fa(token: str = Depends(oauth2_scheme)):
    """
    Habilitar autenticación de dos factores.
    Retorna el secreto y QR para Google Authenticator.
    """
    secret = generate_totp_secret()
    
    # Generar URI para QR
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name="usuario@sicutra.com",  # TODO: Email del usuario
        issuer_name=settings.totp_issuer
    )
    
    # TODO: Guardar secreto en DB (sin activar aún)
    
    return {
        "secret": secret,
        "qr_uri": provisioning_uri,
        "message": "Escanea el QR con Google Authenticator y confirma con el código"
    }


@router.post("/2fa/confirm")
async def confirm_2fa(code: str, token: str = Depends(oauth2_scheme)):
    """
    Confirmar y activar 2FA con el código de verificación.
    """
    # TODO: Obtener secreto temporal de DB
    secret = "JBSWY3DPEHPK3PXP"  # Placeholder
    
    if not verify_totp(secret, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código incorrecto"
        )
    
    # TODO: Activar 2FA en DB
    
    return {"message": "2FA activado correctamente"}
