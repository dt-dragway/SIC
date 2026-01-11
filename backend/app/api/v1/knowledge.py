"""
SIC Ultra - Endpoints de Base de Conocimientos

Gestiona la educación continua del agente:
- Subir libros de trading y finanzas
- Buscar conocimiento
- Ver estadísticas de aprendizaje
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import shutil

from app.api.v1.auth import oauth2_scheme, verify_token
from app.ml.knowledge_base import (
    get_knowledge_base, 
    get_ollama_rag,
    BOOKS_DIR
)


router = APIRouter()


# === Schemas ===

class AddBookRequest(BaseModel):
    title: str
    category: str = "trading"  # trading, finanzas, psicologia, analisis_tecnico


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    category: Optional[str] = None


# === Endpoints ===

@router.post("/upload-book")
async def upload_book(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    category: str = "trading",
    token: str = Depends(oauth2_scheme)
):
    """
    📚 Subir un libro para que el agente aprenda.
    
    Formatos soportados: PDF, DOCX, TXT, MD
    
    Categorías:
    - trading: Estrategias de trading
    - finanzas: Análisis financiero
    - psicologia: Psicología del trader
    - analisis_tecnico: Indicadores y patrones
    - p2p: Mercado P2P y arbitraje
    """
    verify_token(token)
    
    # Verificar extensión
    allowed_extensions = [".pdf", ".docx", ".txt", ".md"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Usa: {allowed_extensions}"
        )
    
    # Guardar archivo
    file_path = os.path.join(BOOKS_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Procesar y añadir a base de conocimientos
    kb = get_knowledge_base()
    
    if not kb.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Base de conocimientos no inicializada. Verifica ChromaDB."
        )
    
    result = kb.add_document(
        file_path=file_path,
        title=title or os.path.splitext(file.filename)[0],
        category=category
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "message": f"📚 Libro '{result['title']}' añadido exitosamente",
        **result
    }


@router.post("/search")
async def search_knowledge(
    request: SearchRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    🔍 Buscar en la base de conocimientos.
    
    El agente usa esto internamente para enriquecer sus análisis.
    """
    verify_token(token)
    
    kb = get_knowledge_base()
    
    if not kb.is_ready:
        return {"results": [], "message": "Base de conocimientos vacía"}
    
    results = kb.search(
        query=request.query,
        n_results=request.n_results,
        category=request.category
    )
    
    return {
        "query": request.query,
        "count": len(results),
        "results": results
    }


@router.get("/stats")
async def get_stats(token: str = Depends(oauth2_scheme)):
    """
    📊 Estadísticas de la base de conocimientos.
    """
    verify_token(token)
    
    kb = get_knowledge_base()
    stats = kb.get_stats()
    
    return {
        **stats,
        "books_directory": BOOKS_DIR,
        "timestamp": datetime.utcnow()
    }


@router.get("/categories")
async def get_categories(token: str = Depends(oauth2_scheme)):
    """
    📁 Categorías disponibles para organizar conocimiento.
    """
    verify_token(token)
    
    return {
        "categories": [
            {"id": "trading", "name": "Estrategias de Trading", "icon": "📈"},
            {"id": "finanzas", "name": "Análisis Financiero", "icon": "💰"},
            {"id": "psicologia", "name": "Psicología del Trader", "icon": "🧠"},
            {"id": "analisis_tecnico", "name": "Análisis Técnico", "icon": "📊"},
            {"id": "p2p", "name": "Mercado P2P y Arbitraje", "icon": "💱"},
            {"id": "criptomonedas", "name": "Fundamentos Crypto", "icon": "🪙"},
            {"id": "gestion_riesgo", "name": "Gestión de Riesgo", "icon": "🛡️"}
        ]
    }


@router.get("/ollama-status")
async def get_ollama_status(token: str = Depends(oauth2_scheme)):
    """
    🤖 Estado de Ollama y base de conocimientos.
    """
    verify_token(token)
    
    ollama = get_ollama_rag()
    kb = get_knowledge_base()
    
    return {
        "ollama": {
            "available": ollama.is_available,
            "model": ollama.model if ollama.is_available else None,
            "message": "Ollama conectado" if ollama.is_available else "Instala Ollama: https://ollama.ai"
        },
        "knowledge_base": {
            "ready": kb.is_ready,
            "documents": kb.get_stats().get("total_chunks", 0) if kb.is_ready else 0
        },
        "timestamp": datetime.utcnow()
    }
