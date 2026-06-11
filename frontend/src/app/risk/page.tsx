'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import {
    Scale,
    Calculator,
    Globe,
    AlertTriangle,
    Info,
    TrendingUp,
    TrendingDown,
    Activity
} from 'lucide-react';

interface KellyResult {
    kelly_percent: number;
    recommended_position: number;
    risk_reward_ratio: number;
    recommendation: string;
}

interface CorrelationData {
    asset_pairs: Record<string, number>;
    interpretation: string;
}

export default function RiskPage() {
    const [winRate, setWinRate] = useState('60');
    const [avgWin, setAvgWin] = useState('150');
    const [avgLoss, setAvgLoss] = useState('100');
    const [kellyResult, setKellyResult] = useState<KellyResult | null>(null);
    const [correlations, setCorrelations] = useState<CorrelationData | null>(null);
    const [loadingCorr, setLoadingCorr] = useState(true);

    useEffect(() => {
        fetchCorrelations();
    }, []);

    const fetchCorrelations = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/risk/macro-correlation', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) setCorrelations(await res.json());
        } catch (error) {
            console.error(error);
        } finally {
            setLoadingCorr(false);
        }
    };

    const calculateKelly = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/risk/kelly-criterion', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    win_rate: parseFloat(winRate),
                    avg_win: parseFloat(avgWin),
                    avg_loss: parseFloat(avgLoss)
                })
            });
            if (res.ok) setKellyResult(await res.json());
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Scale size={32} className="text-amber-400" />
                        Gestión de Riesgo & Macro
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Protege tu capital con herramientas matemáticas y análisis de contexto global
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Kelly Criterion Section */}
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Calculator size={20} className="text-amber-400" />
                            Calculadora de Kelly Criterion
                        </h2>

                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Win Rate (%)</label>
                                    <input
                                        type="number"
                                        value={winRate}
                                        onChange={(e) => setWinRate(e.target.value)}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Promedio Ganador ($)</label>
                                    <input
                                        type="number"
                                        value={avgWin}
                                        onChange={(e) => setAvgWin(e.target.value)}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Promedio Perdedor ($)</label>
                                    <input
                                        type="number"
                                        value={avgLoss}
                                        onChange={(e) => setAvgLoss(e.target.value)}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white font-mono"
                                    />
                                </div>
                            </div>

                            <button
                                onClick={calculateKelly}
                                className="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white font-bold rounded-xl hover:opacity-90 transition-all shadow-lg shadow-amber-500/10"
                            >
                                Calcular Tamaño de Posición
                            </button>

                            {kellyResult && (
                                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 space-y-3">
                                    <div className="flex justify-between items-end">
                                        <div>
                                            <p className="text-xs text-amber-400/60 uppercase font-bold">Posición Recomendada</p>
                                            <p className="text-3xl font-bold text-amber-400 font-mono">
                                                {kellyResult.recommended_position.toFixed(1)}%
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-[10px] text-slate-500 uppercase">Risk/Reward</p>
                                            <p className="text-lg font-bold text-white font-mono">1 : {kellyResult.risk_reward_ratio.toFixed(2)}</p>
                                        </div>
                                    </div>
                                    <div className="pt-3 border-t border-amber-500/10">
                                        <p className="text-sm text-slate-300 flex items-start gap-2">
                                            <Info size={16} className="text-amber-400 mt-0.5" />
                                            {kellyResult.recommendation}
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Macro Correlations Section */}
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Globe size={20} className="text-cyan-400" />
                            Mapa de Correlaciones Macro
                        </h2>

                        {loadingCorr ? (
                            <div className="h-64 flex flex-col items-center justify-center">
                                <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mb-2"></div>
                                <p className="text-xs text-slate-500">Analizando mercados financieros...</p>
                            </div>
                        ) : correlations && (
                            <div className="space-y-6">
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                    {Object.entries(correlations.asset_pairs).map(([pair, value]) => (
                                        <div key={pair} className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                                            <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">{pair}</p>
                                            <div className="flex items-center justify-between">
                                                <span className={`text-lg font-bold font-mono ${value > 0.6 ? 'text-emerald-400' :
                                                    value < -0.4 ? 'text-rose-400' : 'text-slate-400'
                                                    }`}>
                                                    {value > 0 ? '+' : ''}{value.toFixed(2)}
                                                </span>
                                                {value > 0.5 ? <TrendingUp size={14} className="text-emerald-500" /> :
                                                    value < -0.5 ? <TrendingDown size={14} className="text-rose-500" /> :
                                                        <Activity size={14} className="text-slate-600" />}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="p-4 rounded-xl bg-cyan-500/5 border border-cyan-500/10">
                                    <h3 className="text-xs font-bold text-cyan-400 uppercase mb-2 flex items-center gap-2">
                                        <Activity size={14} /> Análisis de Contexto
                                    </h3>
                                    <div className="text-[11px] text-slate-400 leading-relaxed whitespace-pre-line">
                                        {correlations.interpretation}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                </div>

                {/* Risk Management Tips (AI Card) */}
                <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-rose-500/5 to-amber-500/5">
                    <div className="flex items-start gap-4">
                        <div className="p-3 rounded-2xl bg-rose-500/20 text-rose-400">
                            <AlertTriangle size={24} />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white mb-1">Las Reglas de Oro de SIC Ultra</h3>
                            <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mt-4 text-sm text-slate-400">
                                <li className="flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                                    Nunca arriesgues más del 2% de tu capital total por trade.
                                </li>
                                <li className="flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                                    Si el DXY (Dólar) está subiendo, el riesgo en cripto aumenta.
                                </li>
                                <li className="flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                                    Usa la calculadora de Kelly para ajustar tu posición según tu win rate.
                                </li>
                                <li className="flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                                    Diversifica en activos con correlación menor a 0.3.
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>

            </div>
        </DashboardLayout>
    );
}
