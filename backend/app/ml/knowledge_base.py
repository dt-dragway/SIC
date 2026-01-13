"""
SIC Ultra - Base de Conocimientos con Ollama

Sistema RAG (Retrieval Augmented Generation) que permite:
1. Cargar libros de trading y finanzas (PDF, TXT, DOCX)
2. Procesar y almacenar en base de datos vectorial
3. Buscar conocimiento relevante para cada análisis
4. Ollama usa este conocimiento para mejorar señales

El agente aprende y evoluciona con cada libro que le das.
"""

import os
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

# ChromaDB para almacenamiento vectorial
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("⚠️ ChromaDB no disponible")

# Sentence Transformers para embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("⚠️ Sentence Transformers no disponible")

# Procesadores de documentos
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# === Configuración ===

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CHROMA_DIR = os.path.join(KNOWLEDGE_DIR, "chroma_db")
BOOKS_DIR = os.path.join(KNOWLEDGE_DIR, "books")

# Crear directorios
os.makedirs(CHROMA_DIR, exist_ok=True)
os.makedirs(BOOKS_DIR, exist_ok=True)


# === Document Processor ===

class DocumentProcessor:
    """
    Procesa documentos de diferentes formatos.
    Soporta: PDF, DOCX, TXT, MD
    """
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extraer texto de cualquier documento soportado"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == ".pdf":
            return DocumentProcessor._extract_pdf(file_path)
        elif extension == ".docx":
            return DocumentProcessor._extract_docx(file_path)
        elif extension in [".txt", ".md"]:
            return DocumentProcessor._extract_text(file_path)
        else:
            raise ValueError(f"Formato no soportado: {extension}")
    
    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 no instalado")
        
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def _extract_docx(file_path: str) -> str:
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx no instalado")
        
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    @staticmethod
    def _extract_text(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Dividir texto en chunks para embeddings.
        
        Args:
            text: Texto completo
            chunk_size: Tamaño aproximado de cada chunk
            overlap: Superposición entre chunks para mantener contexto
        """
        words = text.split()
        chunks = []
        
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - overlap
        
        return chunks


# === Knowledge Base ===

class KnowledgeBase:
    """
    Base de conocimientos vectorial.
    
    Almacena embeddings de todos los documentos para
    búsqueda semántica rápida.
    """
    
    def __init__(self):
        self.embedding_model = None
        self.client = None
        self.collection = None
        
        self._initialize()
    
    def _initialize(self):
        """Inicializar modelos y base de datos"""
        if not CHROMADB_AVAILABLE:
            logger.error("ChromaDB no disponible")
            return
        
        if not EMBEDDINGS_AVAILABLE:
            logger.error("Sentence Transformers no disponible")
            return
        
        try:
            # Modelo de embeddings (multilingüe, soporta español)
            logger.info("📚 Cargando modelo de embeddings...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            # Cliente ChromaDB persistente
            self.client = chromadb.PersistentClient(path=CHROMA_DIR)
            
            # Colección para trading
            self.collection = self.client.get_or_create_collection(
                name="trading_knowledge",
                metadata={"description": "Base de conocimientos de trading y finanzas"}
            )
            
            logger.success(f"✅ Base de conocimientos inicializada. Documentos: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Error inicializando knowledge base: {e}")
    
    @property
    def is_ready(self) -> bool:
        return self.collection is not None
    
    def add_document(
        self, 
        file_path: str,
        title: Optional[str] = None,
        category: str = "general"
    ) -> Dict:
        """
        Añadir un documento a la base de conocimientos.
        
        Args:
            file_path: Ruta al archivo (PDF, DOCX, TXT)
            title: Título del documento
            category: Categoría (trading, finanzas, psicologia, etc.)
        """
        if not self.is_ready:
            return {"error": "Base de conocimientos no inicializada"}
        
        path = Path(file_path)
        if not path.exists():
            return {"error": f"Archivo no encontrado: {file_path}"}
        
        # Extraer texto
        try:
            text = DocumentProcessor.extract_text(file_path)
            logger.info(f"📄 Texto extraído: {len(text)} caracteres")
        except Exception as e:
            return {"error": f"Error extrayendo texto: {e}"}
        
        # Dividir en chunks
        chunks = DocumentProcessor.chunk_text(text, chunk_size=500, overlap=100)
        logger.info(f"📝 Chunks creados: {len(chunks)}")
        
        # Crear embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Generar IDs únicos
        doc_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # Metadatos
        title = title or path.stem
        metadatas = [
            {
                "source": path.name,
                "title": title,
                "category": category,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "added_at": datetime.utcnow().isoformat()
            }
            for i in range(len(chunks))
        ]
        
        # Añadir a ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        logger.success(f"✅ Documento añadido: {title} ({len(chunks)} chunks)")
        
        return {
            "success": True,
            "title": title,
            "category": category,
            "chunks": len(chunks),
            "total_documents": self.collection.count()
        }
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Buscar conocimiento relevante.
        
        Args:
            query: Pregunta o contexto de búsqueda
            n_results: Número de resultados
            category: Filtrar por categoría
        """
        if not self.is_ready:
            return []
        
        # Generar embedding de la query
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Filtro por categoría
        where = {"category": category} if category else None
        
        # Buscar
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # Formatear resultados
        formatted = []
        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "content": doc,
                "source": results["metadatas"][0][i]["source"],
                "title": results["metadatas"][0][i]["title"],
                "category": results["metadatas"][0][i]["category"],
                "relevance": round(1 - results["distances"][0][i], 3)  # Distancia a similitud
            })
        
        return formatted
    
    def get_trading_context(self, market_situation: str) -> str:
        """
        Obtener contexto de trading relevante para una situación.
        
        Este método es usado por Ollama para enriquecer sus análisis
        con conocimiento de los libros.
        """
        # Buscar conocimiento relevante
        results = self.search(market_situation, n_results=3)
        
        if not results:
            return "No hay conocimiento relevante en la base de conocimientos."
        
        context = "📚 CONOCIMIENTO RELEVANTE DE LA BASE DE DATOS:\n\n"
        
        for i, r in enumerate(results, 1):
            context += f"[{i}] De '{r['title']}' ({r['category']}):\n"
            context += f"{r['content'][:500]}...\n\n"
        
        return context
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de la base de conocimientos"""
        if not self.is_ready:
            return {"status": "not_ready", "documents": 0}
        
        # Obtener todos los metadatos
        all_data = self.collection.get(include=["metadatas"])
        
        categories = {}
        sources = set()
        
        for meta in all_data["metadatas"]:
            cat = meta.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            sources.add(meta.get("source", "unknown"))
        
        return {
            "status": "ready",
            "total_chunks": self.collection.count(),
            "unique_documents": len(sources),
            "categories": categories,
            "documents": list(sources)
        }


# === Ollama con RAG ===

from app.config import settings

# ... imports ...

# ... inside OllamaWithKnowledge ...

class OllamaWithKnowledge:
    """
    Ollama potenciado con base de conocimientos.
    
    Antes de responder, busca conocimiento relevante
    en los libros que le has dado.
    """
    
    BASE_URL = "http://localhost:11434/api/generate"
    
    def __init__(self, model: str = None):
        self.model = model or settings.ollama_model
        self.knowledge = KnowledgeBase()
    
    @property
    def is_available(self) -> bool:
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            return response.status_code == 200
        except:
            return False
    
    async def analyze_with_knowledge(
        self,
        symbol: str,
        price: float,
        indicators: Dict,
        patterns: List[str]
    ) -> Optional[Dict]:
        """
        Análisis de mercado usando conocimiento de libros.
        """
        if not self.is_available:
            return None
        
        # Construir descripción de la situación
        situation = f"""
        Análisis de {symbol} a ${price}.
        RSI: {indicators.get('rsi', 'N/A')}, 
        MACD: {'positivo' if indicators.get('macd_hist', 0) > 0 else 'negativo'},
        Tendencia: {indicators.get('trend', 'N/A')}.
        Patrones: {', '.join(patterns) if patterns else 'ninguno'}.
        """
        
        # Buscar conocimiento relevante
        knowledge_context = self.knowledge.get_trading_context(situation)
        
        # Construir prompt enriquecido
        prompt = f"""Eres un experto en trading con décadas de experiencia.

{knowledge_context}

SITUACIÓN ACTUAL DEL MERCADO:
{situation}

Basándote en tu conocimiento de los libros de trading y la situación actual,
proporciona:
1. SEÑAL: BUY, SELL o HOLD
2. CONFIANZA: porcentaje (0-100)
3. RAZONAMIENTO: basado en los libros y la situación
4. GESTIÓN DE RIESGO: stop-loss y take-profit sugeridos

Responde en español, sé conciso pero preciso.
"""
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "analysis": data.get("response", ""),
                        "model": self.model,
                        "knowledge_used": len(self.knowledge.search(situation, 3)) > 0,
                        "timestamp": datetime.utcnow()
                    }
                    
        except Exception as e:
            logger.error(f"Error en Ollama: {e}")
        
        return None


# === API para gestionar conocimientos ===

def add_book(file_path: str, title: str = None, category: str = "trading") -> Dict:
    """Añadir un libro a la base de conocimientos"""
    kb = KnowledgeBase()
    return kb.add_document(file_path, title, category)


def search_knowledge(query: str, n_results: int = 5) -> List[Dict]:
    """Buscar en la base de conocimientos"""
    kb = KnowledgeBase()
    return kb.search(query, n_results)


def get_knowledge_stats() -> Dict:
    """Obtener estadísticas de la base de conocimientos"""
    kb = KnowledgeBase()
    return kb.get_stats()


# === Singletons ===

_knowledge_base: Optional[KnowledgeBase] = None
_ollama_rag: Optional[OllamaWithKnowledge] = None


def get_knowledge_base() -> KnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base


def get_ollama_rag() -> OllamaWithKnowledge:
    global _ollama_rag
    if _ollama_rag is None:
        _ollama_rag = OllamaWithKnowledge()
    return _ollama_rag
