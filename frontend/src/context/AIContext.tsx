'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { DEFAULT_SYMBOL } from '../lib/constants';

interface AIAnalysis {
    symbol: string;  // Símbolo de la cripto analizada (BTC, ETH, etc.)
    signal: 'BUY' | 'SELL' | 'HOLD' | 'LONG' | 'SHORT';
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

interface AIContextType {
    analysis: AIAnalysis | null;
    loading: boolean;
    status: OllamaStatus | null;
    isBrainOpen: boolean;
    toggleBrain: () => void;
    analyzeMarket: (symbol: string) => Promise<void>;
    checkStatus: () => Promise<void>;
}

const AIContext = createContext<AIContextType | undefined>(undefined);

export function AIProvider({ children }: { children: ReactNode }) {
    const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState<OllamaStatus | null>(null);
    const [symbol, setSymbol] = useState(DEFAULT_SYMBOL); // Global Symbol Focus
    const [mounted, setMounted] = useState(false);

    // Track mount state for client-side only operations
    useEffect(() => {
        setMounted(true);
        // Hydrate from localStorage
        const cachedAnalysis = localStorage.getItem('sic_ai_analysis');
        if (cachedAnalysis) {
            try {
                setAnalysis(JSON.parse(cachedAnalysis));
            } catch (e) {
                console.error("Failed to parse cached AI analysis");
            }
        }
    }, []);

    // Persist analysis changes
    useEffect(() => {
        if (analysis) {
            localStorage.setItem('sic_ai_analysis', JSON.stringify(analysis));
        }
    }, [analysis]);

    // Obtener estado de los modelos
    const checkStatus = async () => {
        if (!mounted) return;
        try {
            const token = localStorage.getItem('token');
            // If we are not logged in, we might not be able to check securely, 
            // but for now let's assume we need token. 
            // If on login page, this might fail silently which is fine.
            if (!token) return;

            const res = await fetch('/api/v1/knowledge/ollama-status', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setStatus(data.ollama);
            }
        } catch (e) {
            console.error("Error checking AI status context", e);
        }
    };

    // Cargar memoria (último análisis)
    const loadMemory = async (sym: string) => {
        if (!mounted) return;
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch(`/api/v1/signals/latest/${sym}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                if (data) {
                    setAnalysis({
                        symbol: sym,  // Símbolo de la cripto
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
            console.error("Error loading AI memory context", e);
        }
    };

    // Analizar mercado - usa el mismo endpoint que AIWidget para consistencia
    const analyzeMarket = async (sym: string) => {
        if (!mounted) return;
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                setLoading(false);
                return;
            }

            // Usar /api/v1/signals/scan como AIWidget para consistencia
            const res = await fetch('/api/v1/signals/scan', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                // Buscar señal para el símbolo o usar la primera disponible
                const signalData = data.signals?.find((s: any) => s.symbol === sym) || data.signals?.[0];

                if (signalData) {
                    setAnalysis({
                        symbol: signalData.symbol || sym,  // Símbolo de la cripto
                        signal: signalData.direction || 'HOLD',
                        confidence: signalData.confidence || 50,
                        reasoning: signalData.reasoning || ['Análisis de mercado completado'],
                        lstm_prediction: signalData.ml_data?.lstm_price || 0,
                        xgboost_class: signalData.ml_data?.xgboost_signal || 'NEUTRAL',
                        timestamp: new Date().toISOString()
                    });
                } else {
                    // No hay señales - mostrar estado neutral
                    setAnalysis({
                        symbol: sym,  // Símbolo por defecto
                        signal: 'HOLD',
                        confidence: 50,
                        reasoning: ['Mercado en consolidación', 'Sin patrones claros detectados'],
                        lstm_prediction: 0,
                        xgboost_class: 'NEUTRAL',
                        timestamp: new Date().toISOString()
                    });
                }
            } else {
                // Respuesta no OK - mostrar HOLD como fallback
                setAnalysis({
                    symbol: sym,  // Símbolo por defecto
                    signal: 'HOLD',
                    confidence: 50,
                    reasoning: ['Analizando condiciones del mercado'],
                    lstm_prediction: 0,
                    xgboost_class: 'NEUTRAL',
                    timestamp: new Date().toISOString()
                });
            }

        } catch (e) {
            console.error("Error analyzing market context", e);
            // En caso de error, mostrar HOLD
            setAnalysis({
                symbol: sym,  // Símbolo por defecto
                signal: 'HOLD',
                confidence: 50,
                reasoning: ['Error de conexión - reintenando...'],
                lstm_prediction: 0,
                xgboost_class: 'NEUTRAL',
                timestamp: new Date().toISOString()
            });
        } finally {
            setLoading(false);
        }
    };

    // Initial Mount Logic (The "Brain" wakes up)
    useEffect(() => {
        // Only run on client after mount
        if (!mounted) return;

        // Only run analysis if we have authentication
        const token = localStorage.getItem('token');
        if (!token) return;

        checkStatus();

        // SIEMPRE hacer análisis fresco en tiempo real
        // Esto garantiza que Sidebar y Dashboard estén 100% sincronizados
        analyzeMarket(symbol);

        // Heartbeat pulse every 30s
        const interval = setInterval(() => {
            const currentToken = localStorage.getItem('token');
            if (!currentToken) return;
            checkStatus();
            analyzeMarket(symbol);
        }, 30000);

        return () => clearInterval(interval);
    }, [symbol, mounted]);

    // Also reload memory if symbol changes (future proofing)
    useEffect(() => {
        if (mounted) {
            loadMemory(symbol);
        }
    }, [symbol, mounted]);

    const [isBrainOpen, setIsBrainOpen] = useState(false);

    const toggleBrain = () => setIsBrainOpen(!isBrainOpen);

    return (
        <AIContext.Provider value={{ analysis, loading, status, isBrainOpen, toggleBrain, analyzeMarket, checkStatus }}>
            {children}
        </AIContext.Provider>
    );
}

export function useAIContext() {
    const context = useContext(AIContext);
    if (context === undefined) {
        throw new Error('useAIContext must be used within an AIProvider');
    }
    return context;
}
