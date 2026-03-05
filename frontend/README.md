# 🎨 SIC Ultra - Frontend Interface (Next.js 14)

La interfaz de usuario de **SIC Ultra** es una terminal de trading moderna, diseñada con un enfoque **Glassmorphism Premium** y optimizada para la visualización de datos complejos en tiempo real.

## 🏗️ Estructura del Proyecto (`src/`)

El frontend utiliza el **App Router** de Next.js 14 para una navegación eficiente y carga optimizada:

```text
src/
├── app/            # Rutas y Páginas (Terminal, IA, Heatmap, etc.)
├── components/     # Componentes modulares organizados por dominio
│   ├── ai/         # Chat y visualizaciones del Agente IA
│   ├── charts/     # Integración con TradingView y gráficos técnicos
│   ├── trading/    # Paneles de ejecución y Order Book
│   ├── neural/     # Visualizaciones de redes neuronales
│   └── ui/         # Componentes base (Botones, inputs, modales)
├── hooks/          # Hooks personalizados de React
├── context/        # Estados globales (Auth, Wallet, Settings)
└── lib/            # Clientes de API y utilidades
```

---

## 🚀 Funcionalidades Principales

- **Terminal Pro**: Gráficos avanzados integrados con datos de microestructura de la API.
- **AI Agent Hub**: Interfaz interactiva para razonar con el Agente de IA.
- **Market Heatmap**: Mapa de calor sectorial con rotación de capital en tiempo real.
- **Sentiment Center**: Dashboard de sentimiento social y de noticias.
- **Risk Management**: Calculadoras de posición y gestión de Stop-Loss dinámico.
- **Trading Journal**: Registro profesional de operaciones con análisis estadístico.

---

## 🛠️ Desarrollo & Despliegue

### Requisitos
- Node.js 20+
- npm o yarn

### Instalación
1. **Instalar dependencias**:
   ```bash
   npm install
   ```

2. **Variables de Entorno**:
   Asegúrate de configurar `NEXT_PUBLIC_API_URL` en tu archivo `.env.local` para apuntar al backend.

3. **Correr en modo desarrollo**:
   ```bash
   npm run dev
   ```

4. **Construir para producción**:
   ```bash
   npm run build
   npm run start
   ```

---

## 💎 Sistema de Diseño
- **Tailwind CSS**: Estilizado rápido y consistente.
- **Glassmorphism**: Capas translúcidas para una estética de terminal de alta gama.
- **Framermotion**: Micro-animaciones fluidas para mejorar la experiencia de usuario.
- **Responsive**: Totalmente adaptado para monitores de escritorio y tablets.
