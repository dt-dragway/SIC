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

export function useAI() {
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

    // Analizar mercado
    const analyzeMarket = async (symbol: string) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error("No autenticado");

            // Llamar al endpoint de análisis (asumimos que existe un endpoint unificado o llamamos a signals)
            const res = await fetch(`/api/v1/signals/analyze/${symbol}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const data = await res.json();

            // Adaptar respuesta al formato UI
            setAnalysis({
                signal: data.signal,
                confidence: data.confidence,
                reasoning: data.reasoning || ["Análisis técnico completado"],
                lstm_prediction: data.ml_data?.lstm_price || 0,
                xgboost_class: data.ml_data?.xgboost_signal || "NEUTRAL",
                timestamp: new Date().toISOString()
            });

        } catch (e) {
            console.error("Error analyzing market", e);
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

    return {
        analysis,
        loading,
        status,
        analyzeMarket,
        checkStatus
    };
}
