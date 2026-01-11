import { useState, useEffect } from 'react';
import { useAI } from '@/hooks/useAI';

export default function AIWidget({ symbol = 'BTCUSDT' }: { symbol?: string }) {
    const { analysis, loading, status, analyzeMarket } = useAI();
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    useEffect(() => {
        // Analizar al montar si hay token
        const token = localStorage.getItem('token');
        if (token) analyzeMarket(symbol);
    }, [symbol]);

    // Colores dinámicos según señal
    const getSignalColor = (signal: string) => {
        switch (signal) {
            case 'BUY': return 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10';
            case 'SELL': return 'text-rose-400 border-rose-500/50 bg-rose-500/10';
            default: return 'text-slate-400 border-slate-500/50 bg-slate-500/10';
        }
    };

    const getConfidenceColor = (score: number) => {
        if (score >= 80) return 'bg-emerald-500';
        if (score >= 50) return 'bg-yellow-500';
        return 'bg-rose-500';
    };

    return (
        <div className="relative group overflow-hidden rounded-2xl border border-white/10 bg-black/40 backdrop-blur-xl p-6 shadow-2xl transition-all hover:border-violet-500/30">

            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="relative h-3 w-3">
                        <span className={`absolute inline-flex h-full w-full animate-ping rounded-full ${status?.available ? 'bg-emerald-400' : 'bg-rose-400'} opacity-75`}></span>
                        <span className={`relative inline-flex h-3 w-3 rounded-full ${status?.available ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                    </div>
                    <h3 className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-xl font-bold text-transparent">
                        AI Neural Engine
                    </h3>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                    {status?.model || 'IA Desconectada'}
                </div>
            </div>

            {/* Main Signal Display */}
            {loading ? (
                <div className="flex h-48 flex-col items-center justify-center gap-4 animate-pulse">
                    <div className="h-12 w-12 rounded-full border-2 border-violet-500 border-t-transparent animate-spin"></div>
                    <p className="text-sm text-violet-300">Procesando millones de datos...</p>
                </div>
            ) : analysis ? (
                <div className="space-y-6">

                    {/* Signal Badge */}
                    <div className={`flex flex-col items-center justify-center rounded-xl border py-6 ${getSignalColor(analysis.signal)}`}>
                        <span className="text-sm font-medium tracking-widest opacity-80">SEÑAL DETECTADA</span>
                        <span className="text-5xl font-black tracking-tighter mt-2">{analysis.signal}</span>
                        <div className="flex items-center gap-2 mt-2 text-sm opacity-80">
                            <span>Confianza:</span>
                            <span className="font-bold">{analysis.confidence}%</span>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div
                            className={`h-full transition-all duration-1000 ${getConfidenceColor(analysis.confidence)}`}
                            style={{ width: `${analysis.confidence}%` }}
                        />
                    </div>

                    {/* Reasoning */}
                    <div className="space-y-2">
                        <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                            <span>🧠</span> Razonamiento del Agente
                        </h4>
                        <div className="max-h-32 overflow-y-auto space-y-2 custom-scrollbar">
                            {analysis.reasoning.map((reason, i) => (
                                <p key={i} className="text-sm text-slate-400 pl-3 border-l-2 border-slate-700">
                                    {reason}
                                </p>
                            ))}
                        </div>
                    </div>

                    {/* Action Button */}
                    <button
                        onClick={() => analyzeMarket(symbol)}
                        className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 font-bold text-white shadow-lg hover:shadow-violet-500/25 transition-all active:scale-95"
                    >
                        🔄 Re-Analizar Mercado
                    </button>
                </div>
            ) : (
                <div className="flex h-48 flex-col items-center justify-center text-center">
                    <p className="text-slate-400 mb-4">Esperando datos de mercado...</p>
                    <button
                        onClick={() => analyzeMarket(symbol)}
                        className="px-6 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-all text-sm font-medium"
                    >
                        Iniciar Análisis
                    </button>
                </div>
            )}
        </div>
    );
}
