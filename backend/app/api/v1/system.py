"""
SIC Ultra - API de Control del Sistema

Endpoints para gestionar servicios del sistema operativo desde el dashboard:
- Estado de Ollama (activo / inactivo)
- Encender / Apagar Ollama
"""

import subprocess
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from app.api.v1.auth import get_current_user
from app.infrastructure.database.models import User

router = APIRouter()


def _run_systemctl(action: str) -> Dict:
    """Ejecuta un comando de systemctl y retorna el resultado."""
    try:
        result = subprocess.run(
            ["sudo", "systemctl", action, "ollama"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Comando systemctl tardó demasiado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando systemctl: {str(e)}")


@router.get("/ollama/status")
async def get_ollama_status(current_user: User = Depends(get_current_user)) -> Dict:
    """
    Retorna el estado actual del servicio Ollama.
    """
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "ollama"],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_active = result.stdout.strip() == "active"
        status_text = result.stdout.strip()

        # Si está activo, también obtenemos el PID e info de memoria
        pid_info = None
        memory_mb = None
        if is_active:
            try:
                show_result = subprocess.run(
                    ["systemctl", "show", "ollama", "--property=MainPID,MemoryCurrent"],
                    capture_output=True, text=True, timeout=5
                )
                for line in show_result.stdout.splitlines():
                    if line.startswith("MainPID="):
                        pid_info = line.split("=")[1]
                    elif line.startswith("MemoryCurrent="):
                        mem_bytes = int(line.split("=")[1])
                        if mem_bytes > 0:
                            memory_mb = round(mem_bytes / (1024 * 1024), 1)
            except Exception:
                pass

        return {
            "is_active": is_active,
            "status": status_text,
            "pid": pid_info,
            "memory_mb": memory_mb,
            "service": "ollama"
        }
    except Exception as e:
        return {
            "is_active": False,
            "status": "unknown",
            "pid": None,
            "memory_mb": None,
            "service": "ollama"
        }


@router.post("/ollama/start")
async def start_ollama(current_user: User = Depends(get_current_user)) -> Dict:
    """
    Enciende el servicio Ollama usando systemctl.
    """
    result = _run_systemctl("start")
    if result["returncode"] != 0:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo iniciar Ollama. Error: {result['stderr']}"
        )
    return {"success": True, "message": "✅ Ollama iniciado correctamente.", "action": "start"}


@router.post("/ollama/stop")
async def stop_ollama(current_user: User = Depends(get_current_user)) -> Dict:
    """
    Apaga el servicio Ollama usando systemctl.
    """
    result = _run_systemctl("stop")
    if result["returncode"] != 0:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo detener Ollama. Error: {result['stderr']}"
        )
    return {"success": True, "message": "🔴 Ollama detenido correctamente.", "action": "stop"}
