"""
SIC Ultra - Endpoints de Entrenamiento ML

Endpoints para entrenar y gestionar los modelos de IA.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd

from app.api.v1.auth import oauth2_scheme, verify_token
from app.infrastructure.binance.client import get_binance_client
from app.ml.models import get_lstm_predictor, get_xgb_classifier, get_ensemble
from app.ml.indicators import calculate_rsi, calculate_macd, calculate_atr


router = APIRouter()


# === Schemas ===

class TrainRequest(BaseModel):
    symbol: str = "BTCUSDT"
    interval: str = "1h"
    limit: int = 500
    epochs: int = 50


class PredictRequest(BaseModel):
    symbol: str
    interval: str = "1h"


# === Helper Functions ===

def get_training_data(symbol: str, interval: str, limit: int) -> pd.DataFrame:
    """
    Obtener datos de Binance y preparar para entrenamiento.
    """
    binance = get_binance_client()
    candles = binance.get_klines(symbol, interval, limit)
    
    if not candles:
        raise ValueError(f"No se pudieron obtener datos de {symbol}")
    
    # Crear DataFrame
    df = pd.DataFrame(candles)
    
    # Calcular indicadores
    closes = df['close'].tolist()
    highs = df['high'].tolist()
    lows = df['low'].tolist()
    
    # RSI
    rsi = calculate_rsi(closes, 14)
    df['rsi'] = [None] * (len(closes) - len(rsi)) + rsi
    
    # MACD
    macd = calculate_macd(closes)
    macd_hist = macd.get('histogram', [])
    df['macd'] = [None] * (len(closes) - len(macd_hist)) + macd_hist
    
    # ATR
    atr = calculate_atr(highs, lows, closes, 14)
    df['atr'] = [None] * (len(closes) - len(atr)) + atr
    
    # Limpiar NaN
    df = df.dropna()
    
    return df


def train_models_background(symbol: str, interval: str, limit: int, epochs: int):
    """
    Función de background para entrenar modelos.
    """
    try:
        df = get_training_data(symbol, interval, limit)
        
        ensemble = get_ensemble()
        result = ensemble.train(df)
        
        return result
    except Exception as e:
        return {"error": str(e)}


# === Endpoints ===

@router.post("/train")
async def train_models(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    🎓 Entrenar modelos de IA con datos históricos.
    
    Este proceso:
    1. Descarga datos históricos de Binance
    2. Calcula indicadores técnicos
    3. Entrena LSTM para predicción de precios
    4. Entrena XGBoost para clasificación de señales
    
    ⚠️ El entrenamiento puede tardar varios minutos.
    """
    verify_token(token)
    
    # Validar símbolo
    binance = get_binance_client()
    price = binance.get_price(request.symbol.upper())
    if not price:
        raise HTTPException(status_code=404, detail=f"Símbolo {request.symbol} no válido")
    
    # Iniciar entrenamiento en background
    background_tasks.add_task(
        train_models_background,
        request.symbol.upper(),
        request.interval,
        request.limit,
        request.epochs
    )
    
    return {
        "message": f"🎓 Entrenamiento iniciado para {request.symbol}",
        "symbol": request.symbol.upper(),
        "interval": request.interval,
        "data_points": request.limit,
        "epochs": request.epochs,
        "status": "TRAINING",
        "note": "El entrenamiento se ejecuta en segundo plano. Use /ml/status para verificar."
    }


@router.get("/predict/{symbol}")
async def get_ml_prediction(
    symbol: str,
    interval: str = "1h",
    token: str = Depends(oauth2_scheme)
):
    """
    🤖 Obtener predicción de los modelos ML.
    
    Combina:
    - LSTM: Predicción numérica del próximo precio
    - XGBoost: Clasificación BUY/SELL/HOLD
    - Ensemble: Consenso de ambos modelos
    """
    verify_token(token)
    
    try:
        df = get_training_data(symbol.upper(), interval, 100)
        
        ensemble = get_ensemble()
        prediction = ensemble.predict(df)
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            **prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lstm/predict/{symbol}")
async def get_lstm_prediction(
    symbol: str,
    interval: str = "1h",
    token: str = Depends(oauth2_scheme)
):
    """
    📈 Predicción de precio con LSTM.
    
    Usa una red neuronal LSTM entrenada para predecir
    el precio del próximo período.
    """
    verify_token(token)
    
    try:
        df = get_training_data(symbol.upper(), interval, 100)
        
        lstm = get_lstm_predictor()
        prediction = lstm.predict(df)
        
        if not prediction:
            return {
                "symbol": symbol.upper(),
                "message": "Modelo LSTM no entrenado. Use POST /ml/train primero.",
                "trained": False
            }
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            **prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/xgboost/predict/{symbol}")
async def get_xgboost_prediction(
    symbol: str,
    interval: str = "1h",
    token: str = Depends(oauth2_scheme)
):
    """
    🌲 Clasificación de señal con XGBoost.
    
    Clasifica la situación actual en:
    - BUY: Momento de compra
    - SELL: Momento de venta
    - HOLD: Mantener posición
    """
    verify_token(token)
    
    try:
        df = get_training_data(symbol.upper(), interval, 100)
        
        xgb = get_xgb_classifier()
        prediction = xgb.predict(df)
        
        if not prediction:
            return {
                "symbol": symbol.upper(),
                "message": "Modelo XGBoost no entrenado. Use POST /ml/train primero.",
                "trained": False
            }
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            **prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_ml_status(token: str = Depends(oauth2_scheme)):
    """
    📊 Estado de los modelos ML.
    """
    verify_token(token)
    
    import os
    models_dir = os.path.join(os.path.dirname(__file__), "..", "ml", "models")
    
    lstm_exists = os.path.exists(os.path.join(models_dir, "lstm_price_predictor.keras"))
    xgb_exists = os.path.exists(os.path.join(models_dir, "xgboost_classifier.json"))
    
    return {
        "models": {
            "lstm": {
                "name": "LSTM Price Predictor",
                "trained": lstm_exists,
                "description": "Red neuronal LSTM para predicción de precios"
            },
            "xgboost": {
                "name": "XGBoost Signal Classifier",
                "trained": xgb_exists,
                "description": "Clasificador para señales BUY/SELL/HOLD"
            }
        },
        "ensemble_available": lstm_exists or xgb_exists,
        "timestamp": datetime.utcnow()
    }
