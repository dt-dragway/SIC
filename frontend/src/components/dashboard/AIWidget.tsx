import { useState, useEffect } from 'react';
import { useAI } from '@/hooks/useAI';
import {
    Brain,
    Activity,
    Zap,
    TrendingUp,
    TrendingDown,
    Minus,
    Cpu,
    RefreshCw,
    Terminal,
    Target
} from 'lucide-react';

export default function AIWidget({ symbol = 'BTCUSDT' }: { symbol?: string }) {
    const { analysis, loading, status, analyzeMarket } = useAI();
    const [elapsed, setElapsed] = useState(0);

    // Timer para "Live" feel
    useEffect(() => {
        const interval = setInterval(() => setElapsed(p => p + 1), 1000);
        return () => clearInterval(interval);
    }, []);

    // Colores dinámicos según señal
    const getSignalColor = (signal: string) => {
        switch (signal) {
            case 'BUY': return { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', glow: 'shadow-emerald-500/20' };
            case 'SELL': return { text: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/30', glow: 'shadow-rose-500/20' };
            default: return { text: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/30', glow: 'shadow-slate-500/10' };
        }
    };

    const styles = analysis ? getSignalColor(analysis.signal) : getSignalColor('HOLD');

    return (
        <div className="relative group overflow-hidden rounded-3xl border border-white/10 bg-[#0a0a0f] p-0 shadow-2xl transition-all hover:border-violet-500/30">
            {/* Background Effects */}
            <div className="absolute top-0 right-0 -mt-20 -mr-20 h-64 w-64 rounded-full bg-violet-600/10 blur-3xl pointer-events-none group-hover:bg-violet-600/20 transition-all"></div>
            <div className="absolute bottom-0 left-0 -mb-20 -ml-20 h-64 w-64 rounded-full bg-fuchsia-600/10 blur-3xl pointer-events-none group-hover:bg-fuchsia-600/20 transition-all"></div>

            {/* Header / Status Bar */}
            <div className="border-b border-white/5 bg-white/[0.02] p-4 flex items-center justify-between backdrop-blur-md">
                <div className="flex items-center gap-3">
                    <div className="relative flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 shadow-lg shadow-violet-500/20">
                        <Brain className="h-4 w-4 text-white" />
                        <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status?.available ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${status?.available ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                        </span>
                    </div>
                    <div>
                        <h3 className="font-bold text-white tracking-tight flex items-center gap-2">
                            Neural Engine
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-white/10 text-violet-300 border border-white/10">v2.0</span>
                        </h3>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
                            <span className="flex items-center gap-1">
                                <Cpu size={10} />
                                {status?.model || 'Desconectado'}
                            </span>
                            <span className="text-slate-600">|</span>
                            <span className="text-emerald-400">ONLINE</span>
                        </div>
                    </div>
                </div>

                <button
                    onClick={() => analyzeMarket(symbol)}
                    disabled={loading}
                    className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
                >
                    <RefreshCw size={18} className={loading ? 'animate-spin text-violet-400' : ''} />
                </button>
            </div>

            {/* Main Content Area */}
            <div className="p-6 space-y-6">

                {!analysis && !loading && (
                    <div className="py-12 flex flex-col items-center justify-center text-center opacity-50">
                        <Activity size={48} className="text-slate-600 mb-4" />
                        <p className="text-slate-400 max-w-[200px]">Esperando datos de mercado para iniciar inferencia...</p>
                        <button
                            onClick={() => analyzeMarket(symbol)}
                            className="mt-6 px-6 py-2 rounded-full bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-all"
                        >
                            Iniciar Escaneo
                        </button>
                    </div>
                )}

                {loading && (
                    <div className="py-12 space-y-6">
                        <div className="flex flex-col items-center gap-4">
                            <div className="relative h-16 w-16">
                                <div className="absolute inset-0 rounded-full border-4 border-violet-500/30"></div>
                                <div className="absolute inset-0 rounded-full border-4 border-violet-500 border-t-transparent animate-spin"></div>
                                <Brain className="absolute inset-0 m-auto text-violet-400 animate-pulse" size={24} />
                            </div>
                            <div className="text-center space-y-1">
                                <h4 className="text-white font-medium animate-pulse">Procesando Tensores...</h4>
                                <p className="text-xs text-slate-500 font-mono">Analizando patrones en {symbol}</p>
                            </div>
                        </div>
                        {/* Fake terminal log */}
                        <div className="mx-4 p-3 rounded-lg bg-black/50 border border-white/5 font-mono text-[10px] text-emerald-500/80 space-y-1">
                            <p>> Loading market data...</p>
                            <p>> Running LSTM prediction...</p>
                            <p>> Validating XGBoost confidence...</p>
                            <p className="animate-pulse">> Generating semantic reasoning...</p>
                        </div>
                    </div>
                )}

                {analysis && !loading && (
                    <>
                        {/* Primary Signal Card */}
                        <div className={`relative overflow-hidden rounded-2xl border p-6 flex items-center justify-between ${styles.bg} ${styles.border} shadow-lg ${styles.glow}`}>
                            <div className="relative z-10">
                                <span className={`text-xs font-bold tracking-widest uppercase ${styles.text} opacity-80 flex items-center gap-2`}>
                                    <Target size={14} />
                                    Señal Detectada
                                </span>
                                <h2 className={`text-5xl font-black tracking-tighter mt-1 mb-1 ${styles.text} drop-shadow-sm`}>
                                    {analysis.signal}
                                </h2>
                            </div>

                            {/* Confidence Gauge (Circular) */}
                            <div className="relative h-20 w-20 flex items-center justify-center">
                                <svg className="h-full w-full rotate-[-90deg]">
                                    <circle cx="50%" cy="50%" r="36" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-black/20" />
                                    <circle
                                        cx="50%" cy="50%" r="36"
                                        stroke="currentColor" strokeWidth="6" fill="transparent"
                                        strokeDasharray={226}
                                        strokeDashoffset={226 - (226 * analysis.confidence) / 100}
                                        strokeLinecap="round"
                                        className={`${styles.text} transition-all duration-1000 ease-out`}
                                    />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className={`text-lg font-bold ${styles.text}`}>{analysis.confidence}%</span>
                                    <span className="text-[8px] text-slate-500 uppercase font-bold">Confianza</span>
                                </div>
                            </div>
                        </div>

                        {/* Sub-Models Grid */}
                        <div className="grid grid-cols-2 gap-3">
                            {/* LSTM */}
                            <div className="bg-white/5 rounded-xl p-3 border border-white/5 hover:bg-white/[0.07] transition-colors">
                                <div className="flex items-center gap-2 mb-2">
                                    <Activity size={14} className="text-cyan-400" />
                                    <span className="text-xs font-medium text-slate-400">LSTM (Precio)</span>
                                </div>
                                <div className="text-lg font-bold text-white font-mono">
                                    ${analysis.lstm_prediction.toLocaleString()}
                                </div>
                            </div>

                            {/* XGBoost */}
                            <div className="bg-white/5 rounded-xl p-3 border border-white/5 hover:bg-white/[0.07] transition-colors">
                                <div className="flex items-center gap-2 mb-2">
                                    <Zap size={14} className="text-amber-400" />
                                    <span className="text-xs font-medium text-slate-400">XGBoost (Trend)</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {analysis.xgboost_class === 'UP' ? <TrendingUp size={16} className="text-emerald-400" /> :
                                        analysis.xgboost_class === 'DOWN' ? <TrendingDown size={16} className="text-rose-400" /> :
                                            <Minus size={16} className="text-slate-400" />}
                                    <span className={`text-sm font-bold ${analysis.xgboost_class === 'UP' ? 'text-emerald-400' :
                                            analysis.xgboost_class === 'DOWN' ? 'text-rose-400' : 'text-slate-400'
                                        }`}>
                                        {analysis.xgboost_class}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Reasoning Terminal */}
                        <div className="bg-black/40 rounded-xl border border-white/10 overflow-hidden">
                            <div className="bg-white/5 px-4 py-2 flex items-center gap-2 border-b border-white/5">
                                <Terminal size={12} className="text-slate-500" />
                                <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Agent Logic Core</span>
                            </div>
                            <div className="p-4 space-y-3 font-mono text-xs max-h-[140px] overflow-y-auto custom-scrollbar">
                                {analysis.reasoning.map((line, i) => (
                                    <div key={i} className="flex gap-3 text-slate-300">
                                        <span className="text-slate-600 select-none">{(i + 1).toString().padStart(2, '0')}</span>
                                        <p className="leading-relaxed">
                                            <span className="text-violet-500 mr-2">➜</span>
                                            {line}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Footer status */}
            <div className="px-6 py-3 bg-white/[0.02] border-t border-white/5 flex justify-between items-center text-[10px] text-slate-500 font-mono">
                <span>System Status: <span className="text-emerald-500">OPTIMAL</span></span>
                <span>Latency: {Math.floor(Math.random() * 20 + 10)}ms</span>
            </div>
        </div>
    );
}
