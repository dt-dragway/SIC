'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Scale, TrendingUp, AlertTriangle } from 'lucide-react';

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

    useEffect(() => {
        fetchCorrelations();
    }, []);

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
            console.error("Error calculating Kelly:", error);
        }
    };

    const fetchCorrelations = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/risk/macro-correlation', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) setCorrelations(await res.json());
        } catch (error) {
            console.error("Error fetching correlations:", error);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Scale size={32} className="text-amber-400" />
                        Risk Management
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Kelly Criterion y Análisis de Correlación Macro
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Kelly Criterion Calculator */}
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Scale size={20} className="text-amber-400" />
                            Kelly Criterion Calculator
                        </h2>

                        <div className="space-y-3 mb-4">
                            <div>
                                <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Win Rate (%)</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={winRate}
                                    onChange={(e) => setWinRate(e.target.value)}
                                    placeholder="60"
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Avg Win ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={avgWin}
                                        onChange={(e) => setAvgWin(e.target.value)}
                                        placeholder="150"
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Avg Loss ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={avgLoss}
                                        onChange={(e) => setAvgLoss(e.target.value)}
                                        placeholder="100"
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={calculateKelly}
                            className="w-full px-6 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-white font-bold hover:opacity-90 transition-all mb-4"
                        >
                            Calcular Kelly
                        </button>

                        {kellyResult && (
                            <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 space-y-3">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Full Kelly:</span>
                                    <span className="text-white font-mono font-bold">{kellyResult.kelly_percent.toFixed(2)}%</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Half Kelly (Recomendado):</span>
                                    <span className="text-amber-400 font-mono font-bold">{kellyResult.recommended_position.toFixed(2)}%</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Risk/Reward:</span>
                                    <span className="text-white font-mono">1:{kellyResult.risk_reward_ratio.toFixed(2)}</span>
                                </div>
                                <div className="pt-3 border-t border-white/10">
                                    <p className="text-xs text-slate-300">{kellyResult.recommendation}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Macro Correlation */}
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingUp size={20} className="text-cyan-400" />
                            Correlación Macro
                        </h2>

                        {correlations ? (
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    {Object.entries(correlations.asset_pairs).map(([pair, corr]) => (
                                        <div key={pair} className="space-y-1">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-slate-400">{pair}</span>
                                                <span className={`font-mono font-bold ${Math.abs(corr) > 0.7 ? 'text-rose-400' :
                                                        Math.abs(corr) > 0.4 ? 'text-amber-400' :
                                                            'text-emerald-400'
                                                    }`}>
                                                    {corr.toFixed(2)}
                                                </span>
                                            </div>
                                            <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full ${Math.abs(corr) > 0.7 ? 'bg-rose-500' :
                                                            Math.abs(corr) > 0.4 ? 'bg-amber-500' :
                                                                'bg-emerald-500'
                                                        }`}
                                                    style={{ width: `${Math.abs(corr) * 100}%` }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
                                    <div className="flex items-start gap-2 mb-2">
                                        <AlertTriangle size={16} className="text-cyan-400 mt-0.5" />
                                        <h3 className="text-sm font-bold text-cyan-300">Interpretación</h3>
                                    </div>
                                    <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                                        {correlations.interpretation}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="py-8 text-center">
                                <div className="h-6 w-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                                <p className="text-xs text-slate-500 mt-2">Cargando correlaciones...</p>
                            </div>
                        )}
                    </div>

                </div>

            </div>
        </DashboardLayout>
    );
}
