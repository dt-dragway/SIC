'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react';
import { DEFAULT_SYMBOL } from '../lib/constants';
import { toast } from 'sonner';
import { Zap, TrendingUp, TrendingDown } from 'lucide-react';

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
    const lastTradeIdRef = useRef<number | null>(null);

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

    // Polling del Centinela CIO para Notificaciones Globales
    const pollSentinelTrades = async () => {
        if (!mounted) return;
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/practice/sentinel-logs?limit=5', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const logs = await res.json();
                if (logs && logs.length > 0) {
                    const latestTrade = logs[0];

                    // Si es la primera vez que cargamos, guardamos el ID sin mostrar toast
                    if (lastTradeIdRef.current === null) {
                        lastTradeIdRef.current = latestTrade.id;
                        return;
                    }

                    // Si el ID es mayor al último visto, hay nuevos trades
                    if (latestTrade.id > lastTradeIdRef.current) {
                        // Procesar todos los trades nuevos
                        const newTrades = logs.filter((l: any) => l.id > (lastTradeIdRef.current || 0)).reverse();

                        newTrades.forEach((trade: any) => {
                            toast.custom((t) => (
                                <div className="bg-[#0B0E14]/95 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-2xl flex items-start gap-4 min-w-[320px] animate-in slide-in-from-right-5">
                                    <div className={`p-2 rounded-xl bg-gradient-to-br ${trade.side === 'BUY' ? 'from-emerald-500 to-teal-600' : 'from-rose-500 to-pink-600'} shadow-lg`}>
                                        {trade.side === 'BUY' ? <TrendingUp size={18} className="text-white" /> : <TrendingDown size={18} className="text-white" />}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex justify-between items-center mb-1">
                                            <div className="flex items-center gap-2">
                                                <h4 className="text-white font-bold text-sm tracking-tight">{trade.side === 'BUY' ? 'Compra' : 'Venta'} Táctica IA</h4>
                                                <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-[8px] text-blue-400 font-bold uppercase tracking-tighter">Sentinel</span>
                                            </div>
                                            <span className="text-[9px] text-slate-500 font-mono italic">Justified</span>
                                        </div>
                                        <p className="text-cyan-400 font-bold text-xs mb-1 font-mono">
                                            {trade.symbol} @ ${trade.price.toLocaleString()}
                                        </p>
                                        <p className="text-slate-300 text-[10px] leading-relaxed line-clamp-2">
                                            {trade.reason}
                                        </p>
                                    </div>
                                    <button onClick={() => toast.dismiss(t)} className="text-slate-600 hover:text-white transition-colors">
                                        <Zap size={12} />
                                    </button>
                                </div>
                            ), {
                                duration: 10000,
                            });
                        });

                        lastTradeIdRef.current = latestTrade.id;
                    }
                }
            }
        } catch (e) {
            console.error("Error polling sentinel trades", e);
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

        // Heartbeat pulse every 30s for analysis, but 10s for Sentinel
        const interval = setInterval(() => {
            const currentToken = localStorage.getItem('token');
            if (!currentToken) return;
            checkStatus();
            analyzeMarket(symbol);
        }, 30000);

        const sentinelInterval = setInterval(() => {
            pollSentinelTrades();
        }, 12000); // Cada 12 segundos para no saturar

        return () => {
            clearInterval(interval);
            clearInterval(sentinelInterval);
        };
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
