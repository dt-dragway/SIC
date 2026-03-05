from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.api.v1.auth import oauth2_scheme, verify_token
from app.services.execution_engine import get_execution_engine

router = APIRouter()

class ExecutionRequest(BaseModel):
    symbol: str = "BTCUSDT"
    side: str = "BUY"
    total_quantity: float
    duration_minutes: int
    algorithm: str = "TWAP" # "TWAP", "VWAP", "POV"

@router.post("/execute")
async def start_advanced_execution(
    request: ExecutionRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Inicia un algoritmo de ejecución avanzada (TWAP/VWAP).
    """
    user_data = verify_token(token)
    user_id = user_data.get("sub") # O como obtengas el ID en tu sistema
    
    engine = get_execution_engine()
    
    if request.algorithm == "TWAP":
        background_tasks.add_task(
            engine.execute_twap, 
            request.symbol, 
            request.side, 
            request.total_quantity, 
            request.duration_minutes,
            user_id
        )
    elif request.algorithm == "VWAP":
        background_tasks.add_task(
            engine.execute_vwap, 
            request.symbol, 
            request.side, 
            request.total_quantity, 
            request.duration_minutes,
            user_id
        )
    else:
        raise HTTPException(status_code=400, detail="Algoritmo no soportado")

    return {
        "status": "started",
        "algorithm": request.algorithm,
        "symbol": request.symbol,
        "side": request.side,
        "total_quantity": request.total_quantity,
        "estimated_completion": f"{request.duration_minutes} minutos"
    }

@router.get("/active-orders")
async def get_active_executions(token: str = Depends(oauth2_scheme)):
    """
    Obtener órdenes algorítmicas en curso.
    """
    verify_token(token)
    # En una implementación real, persistiríamos esto en Redis/DB
    return {"orders": []}
