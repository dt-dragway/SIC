'use client';

import { useState } from 'react';
import { Sparkles, Send, Loader2 } from 'lucide-react';

interface AIAnalysis {
    symbol: string;
    query: string;
    tools_used: string[];
    recommendation: {
        action: string;
        confidence: number;
        reasoning: string[];
        position_size: number;
        alerts: any[];
    };
    data: any;
    timestamp: string;
}

export default function InstitutionalAssistant() {
    const [query, setQuery] = useState('');
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);

    const analyzeWithAI = async () => {
        if (!query.trim()) return;

        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/ai/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol,
                    query,
                    context: null
                })
            });

            if (res.ok) {
                const data = await res.json();
                setAnalysis(data);
            }
        } catch (error) {
            console.error("Error analyzing:", error);
        } finally {
            setLoading(false);
        }
    };

    const getActionColor = (action: string) => {
        if (action === 'BUY') return 'text-emerald-400';
        if (action === 'SELL') return 'text-rose-400';
        return 'text-slate-400';
    };

    return (
        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles size={20} className="text-purple-400" />
                Asistente IA Institucional
            </h2>

            {/* Input */}
            <div className="space-y-3 mb-4">
                <div className="flex gap-2">
                    <select
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                    >
                        <option value="BTCUSDT">BTC</option>
                        <option value="ETHUSDT">ETH</option>
                        <option value="SOLUSDT">SOL</option>
                    </select>

                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && analyzeWithAI()}
                        placeholder="Ej: ¿Debería comprar BTC ahora?"
                        className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder:text-slate-500"
                    />

                    <button
                        onClick={analyzeWithAI}
                        disabled={loading || !query.trim()}
                        className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold hover:opacity-90 transition-all disabled:opacity-50"
                    >
                        {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                    </button>
                </div>

                {/* Quick queries */}
                <div className="flex gap-2 flex-wrap">
                    <button
                        onClick={() => setQuery('¿Debería comprar ahora?')}
                        className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-slate-400"
                    >
                        Análisis de compra
                    </button>
                    <button
                        onClick={() => setQuery('¿Cómo puedo ganar sin riesgo?')}
                        className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-slate-400"
                    >
                        Delta Neutral
                    </button>
                    <button
                        onClick={() => setQuery('¿Hay movimientos de ballenas?')}
                        className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-slate-400"
                    >
                        Whale Alerts
                    </button>
                </div>
            </div>

            {/* Analysis Result */}
            {analysis && (
                <div className="space-y-4">
                    {/* Tools Used */}
                    <div className="flex gap-2 flex-wrap">
                        {analysis.tools_used.map((tool, i) => (
                            <span key={i} className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                                {tool}
                            </span>
                        ))}
                    </div>

                    {/* Recommendation */}
                    <div className={`p-4 rounded-lg border ${analysis.recommendation.action === 'BUY' ? 'bg-emerald-500/10 border-emerald-500/30' :
                            analysis.recommendation.action === 'SELL' ? 'bg-rose-500/10 border-rose-500/30' :
                                'bg-slate-500/10 border-slate-500/30'
                        }`}>
                        <div className="flex justify-between items-center mb-3">
                            <span className={`text-lg font-bold ${getActionColor(analysis.recommendation.action)}`}>
                                {analysis.recommendation.action}
                            </span>
                            <span className="text-sm text-slate-400">
                                Confianza: <span className="text-white font-bold">{analysis.recommendation.confidence}%</span>
                            </span>
                        </div>

                        {analysis.recommendation.position_size > 0 && (
                            <div className="mb-2 text-sm">
                                <span className="text-slate-400">Tamaño recomendado: </span>
                                <span className="text-white font-bold">{analysis.recommendation.position_size.toFixed(1)}%</span>
                                <span className="text-slate-500"> del capital</span>
                            </div>
                        )}

                        <div className="space-y-1">
                            {analysis.recommendation.reasoning.map((reason, i) => (
                                <p key={i} className="text-xs text-slate-300">{reason}</p>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {!analysis && !loading && (
                <div className="py-8 text-center">
                    <Sparkles size={32} className="text-slate-600 mx-auto mb-2" />
                    <p className="text-xs text-slate-500">Pregunta algo y la IA usará las herramientas institucionales automáticamente</p>
                </div>
            )}
        </div>
    );
}
