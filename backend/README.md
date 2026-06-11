# 🧠 SIC Ultra - Backend Core (FastAPI)

Este es el núcleo de inteligencia y ejecución de **SIC Ultra**. Una arquitectura de servicios de alto rendimiento construida con Python y orientada a la toma de decisiones institucionales.

## 🏛️ Arquitectura del Sistema

El backend sigue una estructura modular limpia:

```text
backend/app/
├── api/             # Endpoints REST (v1)
├── infrastructure/  # Conectores (DB, APIs externas como Binance)
├── ml/              # El "Cerebro" (Agentes, Modelos, RAG)
├── services/        # Lógica de negocio y orquestación
├── middleware/      # Seguridad, CORS, Logging
├── config.py        # Configuración centralizada (Pydantic Settings)
└── main.py          # Punto de entrada de la aplicación
```

---

## 🚀 Componentes de Inteligencia (ML Engine)

Ubicado en `app/ml/`, este ecosistema permite el análisis omni-consciente:

- **`trading_agent.py`**: El orquestador principal que coordina todas las señales.
- **`llm_connector.py`**: Interfaz con **Ollama / Llama 3.2** para razonamiento natural.
- **`knowledge_base.py`**: Sistema RAG que permite al agente aprender de documentos externos.
- **`signal_generator.py`**: Generador de señales técnicas basado en microestructura.
- **`models.py`**: Implementaciones de Deep Learning (**LSTM**) y Gradient Boosting (**XGBoost**).
- **`candlestick_analyzer.py`**: Análisis avanzado de patrones de velas.

---

## 🛠️ Instalación & Desarrollo

### Requisitos
- Python 3.12+
- PostgreSQL (con soporte de vectores para RAG)
- Redis (para caché y colas)

### Pasos
1. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux
   pip install -r requirements.txt
   ```

2. **Configurar Variables**:
   Crea un archivo `.env` basado en `.env.template`.

3. **Migraciones**:
   Si usas Prisma o SQLAlchemy para el esquema:
   ```bash
   # Ejemplo si hay script de setup
   ./setup_db.sh
   ```

4. **Ejecutar Servidor**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 🧪 Pruebas (Testing)

El sistema utiliza `pytest` para asegurar la integridad de los algoritmos de trading:

```bash
# Correr todos los tests
pytest

# Correr tests con cobertura
pytest --cov=app tests/
```

---

## 🛡️ Seguridad & Rendimiento
- **JWT Authentication**: Todas las rutas críticas están protegidas.
- **Rate Limiting**: Protección contra ataques de fuerza bruta en los endpoints de la API.
- **Logging Asíncrono**: Registro detallado de cada operación institucional sin afectar la latencia.
