# 🦅 SIC Ultra - Sistema Integral Criptofinanciero

**Tu Asistente de Trading Profesional con Inteligencia Artificial Avanzada**

![Status](https://img.shields.io/badge/Status-Activo-success)
![AI](https://img.shields.io/badge/AI-Ollama%20%2B%20TensorFlow-blueviolet)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js%2014-black)

SIC Ultra es una plataforma de trading algorítmico y manual diseñada para minimizar riesgos y maximizar ganancias mediante el uso de modelos de Machine Learning de última generación y razonamiento lógico LLM.

---

## 🚀 Características Principales

### 🧠 Cerebro Digital (AI Core)
- **Razonamiento Lógico**: Integración con **Ollama (Llama 3.2)** para explicar el "por qué" de cada movimiento.
- **Predicción de Precios**: Redes neuronales **LSTM** (Long Short-Term Memory) entrenadas con TensorFlow.
- **Clasificación de Señales**: Modelo **XGBoost** para determinar puntos óptimos de entrada/salida.
- **Aprendizaje RAG**: El agente lee libros PDF que subes para aprender nuevas estrategias (Retrieval Augmented Generation).

### 💱 Inteligencia P2P (Arbitraje)
- **Panel "Golden Opportunities"**: Detecta automáticamente brechas de precio para arbitraje inmediato.
- **Análisis de Traders**: Identifica a los mejores comerciantes para copiar estrategias.
- **Timing Optimization**: Sugiere las mejores horas del día para operar con base en liquidez y spreads.

### 🛡️ Seguridad y Riesgo (7 Capas)
1. Límites de pérdida diaria (-5%)
2. Stop-Loss obligatorio en todas las órdenes
3. Tamaño máximo de posición dinámico
4. Validación de volatilidad extrema
5. 2FA (Autenticación de Dos Factores)
6. Encriptación JWT + AES
7. Modo Práctica Sandbox ($100 virtuales)

### 💻 Interfaz Premium
- Diseño **Glassmorphism** oscuro profesional.
- Gráficos interactivos en tiempo real.
- Notificaciones de señales instantáneas.
- **Widget IA**: Visualización del pensamiento del agente en el dashboard.

---

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Base de Datos**: PostgreSQL 16
- **Cache**: Redis
- **ML/AI**: TensorFlow, XGBoost, Scikit-learn, LangChain, ChromaDB
- **LLM**: Ollama (Llama 3)
- **Infraestructura**: Docker, Docker Compose

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS 3
- **Estado**: React Hooks
- **Gráficos**: TradingView Charting Library (lightweight)

---

## 📦 Instalación

### Prerrequisitos
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- [Ollama](https://ollama.ai) (para el agente de razonamiento)

### Pasos Iniciales

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/sic-ultra.git
   cd sic-ultra
   ```

2. **Configurar entorno**
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales de Binance y Base de Datos
   ```

3. **Iniciar servicios (Backend + DB)**
   ```bash
   docker-compose up -d
   ```
   *O manualmente:*
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **Iniciar Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Activar IA (Ollama)**
   ```bash
   ollama serve
   ollama pull llama3
   ```

---

## 🎮 Guía de Uso

### 1. Modo Práctica (Recomendado)
Al iniciar, el sistema estará en **Modo Práctica** por defecto. Tienes $100 USD virtuales.
- Ve a `/trading` y ejecuta órdenes para probar estrategias.
- El agente analizará tus movimientos y sugerirá mejoras.

### 2. Alimentar al Agente
- Ve a **Biblioteca** (`/knowledge`).
- Sube libros PDF sobre trading (ej: "Trading en la Zona", "Análisis Técnico").
- El agente procesará el texto y usará ese conocimiento en sus señales.

### 3. P2P Radar
- Ve a **P2P** (`/p2p`).
- Revisa las tarjetas doradas en la parte superior.
- Si ves una oportunidad de arbitraje con **Score > 90**, ¡actúa rápido!

### 4. Modo Real (¡Precaución!)
- Configura tus API Keys de Binance en `.env`.
- Cambia el toggle a **⚔️ Real**.
- El sistema aplicará las 7 capas de protección automáticamente.

---

## 🤝 Contribución

Proyecto privado desarrollado para **SIC Ultra**.
Si deseas contribuir:
1. Fork del proyecto
2. Crea tu Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al Branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es propietario y confidencial.
© 2026 SIC Ultra. Todos los derechos reservados.
