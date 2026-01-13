'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

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
    const [symbol, setSymbol] = useState('BTCUSDT'); // Global Symbol Focus

    // Obtener estado de los modelos
    const checkStatus = async () => {
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

    // Analizar mercado
    const analyzeMarket = async (sym: string) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error("No autenticado");

            const res = await fetch(`/api/v1/signals/analyze/${sym}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                setAnalysis({
                    signal: data.signal,
                    confidence: data.confidence,
                    reasoning: data.reasoning || ["Análisis técnico completado"],
                    lstm_prediction: data.ml_data?.lstm_price || 0,
                    xgboost_class: data.ml_data?.xgboost_signal || "NEUTRAL",
                    timestamp: new Date().toISOString()
                });
            }

        } catch (e) {
            console.error("Error analyzing market context", e);
        } finally {
            setLoading(false);
        }
    };

    // Initial Mount Logic (The "Brain" wakes up)
    useEffect(() => {
        // Only run on client
        if (typeof window === 'undefined') return;

        checkStatus();
        loadMemory(symbol).then(() => {
            // Si no hay memoria, o para refrezcar, iniciamos análisis
            analyzeMarket(symbol);
        });

        // Heartbeat pulse every 30s
        // Heartbeat pulse every 30s
        const interval = setInterval(() => {
            checkStatus();
            analyzeMarket(symbol);
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    // Also reload memory if symbol changes (future proofing)
    useEffect(() => {
        if (typeof window !== 'undefined') {
            loadMemory(symbol);
        }
    }, [symbol]);

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
