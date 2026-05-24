import { useState, useEffect } from 'react';

interface AIAnalysis {
    signal: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    reasoning: string[];
    lstm_prediction: number;
    xgboost_class: string;
    timestamp: string;
}

interface OllamaStatus {
    available: boolean;
    model: string | null;
    message: string;
}

export function useAI(symbol: string = 'BTCUSDT') {
    const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState<OllamaStatus | null>(null);

    // Obtener estado de los modelos
    const checkStatus = async () => {
        try {
            // Nota: Necesitas añadir el token de auth en los headers en una implementación real
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/knowledge/ollama-status', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            setStatus(data.ollama);
        } catch (e) {
            console.error("Error checking AI status", e);
        }
    };

    // Cargar memoria (último análisis)
    const loadMemory = async (symbol: string) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch(`/api/v1/signals/latest/${symbol}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                if (data) {
                    setAnalysis({
                        signal: data.signal,
                        confidence: data.confidence,
                        reasoning: data.reasoning || [],
                        lstm_prediction: data.ml_data?.lstm_price || 0,
                        xgboost_class: data.ml_data?.xgboost_signal || "NEUTRAL",
                        timestamp: data.timestamp
                    });
                }
            }
        } catch (e) {
            console.error("Error loading AI memory", e);
        }
    };

    // Analizar mercado
    const analyzeMarket = async (symbol: string) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) return; // Exit silently if no token

            const res = await fetch(`/api/v1/signals/analyze/${symbol}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // Handle 404 as HOLD signal (no clear signal available)
            if (res.status === 404) {
                setAnalysis({
                    signal: 'HOLD',
                    confidence: 50,
                    reasoning: ["Sin señal clara en este momento", "El mercado está en consolidación"],
                    lstm_prediction: 0,
                    xgboost_class: "NEUTRAL",
                    timestamp: new Date().toISOString()
                });
                return;
            }

            if (!res.ok) {
                // Log non-404 errors but don't spam console
                if (res.status !== 401) {
                    console.error(`Signal API error: ${res.status}`);
                }
                return;
            }

            const data = await res.json();

            // Adaptar respuesta al formato UI (signal o direction)
            setAnalysis({
                signal: data.direction || data.signal || 'HOLD',
                confidence: data.confidence || 50,
                reasoning: data.reasoning || ["Análisis técnico completado"],
                lstm_prediction: data.ml_data?.lstm_price || 0,
                xgboost_class: data.ml_data?.xgboost_signal || "NEUTRAL",
                timestamp: new Date().toISOString()
            });

        } catch (e) {
            // Silent fail - don't spam console with expected errors
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkStatus();
        // Polling cada 30s para verificar estado
        const interval = setInterval(checkStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    // Cargar memoria al cambiar de símbolo
    useEffect(() => {
        if (symbol) loadMemory(symbol);
    }, [symbol]);

    return {
        analysis,
        loading,
        status,
        analyzeMarket,
        checkStatus
    };
}
