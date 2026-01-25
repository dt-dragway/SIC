import { useAIContext } from '@/context/AIContext';
import {
    Brain,
    Cpu,
    RefreshCw,
    Terminal,
    Target
} from 'lucide-react';

export default function AIWidget({ symbol = 'BTCUSDT' }: { symbol?: string }) {
    // Usar el contexto compartido - ahora sincronizado con Sidebar
    const { analysis, loading, analyzeMarket, status } = useAIContext();

    const handleRefresh = () => {
        analyzeMarket(symbol);
    };

    // Colores dinámicos según señal
    const getSignalColor = (signal: string) => {
        switch (signal) {
            case 'LONG':
            case 'BUY':
                return {
                    text: 'text-emerald-400',
                    bg: 'bg-emerald-500/10',
                    border: 'border-emerald-500/30',
                    glow: 'shadow-emerald-500/20'
                };
            case 'SHORT':
            case 'SELL':
                return {
                    text: 'text-rose-400',
                    bg: 'bg-rose-500/10',
                    border: 'border-rose-500/30',
                    glow: 'shadow-rose-500/20'
                };
            default:
                return {
                    text: 'text-slate-400',
                    bg: 'bg-slate-500/10',
                    border: 'border-slate-500/30',
                    glow: 'shadow-slate-500/10'
                };
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
                            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${analysis ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${analysis ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
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
                                Trading Agent
                            </span>
                            <span className="text-slate-600">|</span>
                            <span className={analysis ? 'text-emerald-400' : 'text-amber-400'}>
                                {analysis ? 'ACTIVO' : 'INICIANDO'}
                            </span>
                        </div>
                    </div>
                </div>

                <button
                    onClick={handleRefresh}
                    disabled={loading}
                    className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
                >
                    <RefreshCw size={18} className={loading ? 'animate-spin text-violet-400' : ''} />
                </button>
            </div>

            {/* Main Content Area */}
            <div className="p-6 space-y-6">

                {loading && (
                    <div className="py-12 space-y-6">
                        <div className="flex flex-col items-center gap-4">
                            <div className="relative h-16 w-16">
                                <div className="absolute inset-0 rounded-full border-4 border-violet-500/30"></div>
                                <div className="absolute inset-0 rounded-full border-4 border-violet-500 border-t-transparent animate-spin"></div>
                                <Brain className="absolute inset-0 m-auto text-violet-400 animate-pulse" size={24} />
                            </div>
                            <div className="text-center space-y-1">
                                <h4 className="text-white font-medium animate-pulse">Analizando Mercado...</h4>
                                <p className="text-xs text-slate-500 font-mono">Procesando {symbol}</p>
                            </div>
                        </div>
                        {/* Terminal log */}
                        <div className="mx-4 p-3 rounded-lg bg-black/50 border border-white/5 font-mono text-[10px] text-emerald-500/80 space-y-1">
                            <p>&gt; Conectando con Binance API...</p>
                            <p>&gt; Calculando indicadores técnicos...</p>
                            <p>&gt; Analizando patrones de mercado...</p>
                            <p className="animate-pulse">&gt; Generando señal...</p>
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
                                    {analysis.signal === 'HOLD' ? 'Mercado Neutral' : 'Señal Detectada'}
                                </span>
                                <h2 className={`text-5xl font-black tracking-tighter mt-1 mb-1 ${styles.text} drop-shadow-sm`}>
                                    {analysis.signal}
                                </h2>
                                {analysis.symbol && (
                                    <p className="text-sm text-slate-400 font-mono">
                                        {analysis.symbol.replace('USDT', '')} • {analysis.lstm_prediction ? `$${analysis.lstm_prediction.toLocaleString()}` : ''}
                                    </p>
                                )}
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
                                    <span className={`text-lg font-bold ${styles.text}`}>{Math.round(analysis.confidence)}%</span>
                                    <span className="text-[8px] text-slate-500 uppercase font-bold">Confianza</span>
                                </div>
                            </div>
                        </div>

                        {/* Reasoning Terminal */}
                        <div className="bg-black/40 rounded-xl border border-white/10 overflow-hidden">
                            <div className="bg-white/5 px-4 py-2 flex items-center gap-2 border-b border-white/5">
                                <Terminal size={12} className="text-slate-500" />
                                <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Análisis IA</span>
                            </div>
                            <div className="p-4 space-y-3 font-mono text-xs max-h-[140px] overflow-y-auto custom-scrollbar">
                                {analysis.reasoning && analysis.reasoning.slice(0, 4).map((line, i) => (
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
                <span>Auto-refresh: 30s</span>
            </div>
        </div>
    );
}
