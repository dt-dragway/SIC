'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import {
    TrendingUp,
    Calculator,
    BarChart3,
    DollarSign,
    AlertCircle,
    CheckCircle2
} from 'lucide-react';

interface BasisOpportunity {
    symbol: string;
    spot_price: number;
    futures_price: number;
    basis_points: number;
    basis_percent: number;
    funding_rate: number;
    apr_estimate: number;
    recommended: boolean;
}

interface HedgeResult {
    symbol: string;
    current_delta: number;
    required_hedge: number;
    recommendation: string;
}

export default function DerivativesPage() {
    const [opportunities, setOpportunities] = useState<BasisOpportunity[]>([]);
    const [hedgeResults, setHedgeResults] = useState<HedgeResult[]>([]);
    const [loading, setLoading] = useState(true);

    // Hedge Calculator Inputs
    const [spotHoldings, setSpotHoldings] = useState<Record<string, string>>({ 'BTCUSDT': '' });

    useEffect(() => {
        fetchOpportunities();
        const interval = setInterval(fetchOpportunities, 60000); // 1 min
        return () => clearInterval(interval);
    }, []);

    const fetchOpportunities = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/derivatives/basis-opportunities', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) setOpportunities(await res.json());
        } catch (error) {
            console.error("Error fetching basis opportunities:", error);
        } finally {
            setLoading(false);
        }
    };

    const calculateHedge = async () => {
        try {
            const token = localStorage.getItem('token');

            // Convert spot holdings to proper format
            const holdings: Record<string, number> = {};
            Object.entries(spotHoldings).forEach(([symbol, amount]) => {
                if (amount && parseFloat(amount) > 0) {
                    holdings[symbol] = parseFloat(amount);
                }
            });

            if (Object.keys(holdings).length === 0) {
                alert("Ingresa al menos una posición Spot");
                return;
            }

            const res = await fetch('/api/v1/derivatives/hedge-calculator', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    spot_holdings: holdings,
                    futures_positions: [] // Usuario puede expandir esto
                })
            });

            if (res.ok) setHedgeResults(await res.json());
        } catch (error) {
            console.error("Error calculating hedge:", error);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent flex items-center gap-3">
                        <BarChart3 size={32} className="text-emerald-400" />
                        Delta Neutral & Derivatives
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Gana funding rates sin asumir riesgo direccional
                    </p>
                </div>

                {/* Basis Trading Opportunities */}
                <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                    <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <TrendingUp size={20} className="text-emerald-400" />
                        Oportunidades de Basis Trading
                    </h2>

                    {loading ? (
                        <div className="py-8 text-center">
                            <div className="h-6 w-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                            <p className="text-xs text-slate-500 mt-2">Escaneando mercados...</p>
                        </div>
                    ) : opportunities.length === 0 ? (
                        <p className="text-slate-600 text-center py-8">No hay oportunidades disponibles</p>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-left text-[10px] uppercase font-bold text-slate-500 border-b border-white/5">
                                        <th className="pb-2">Par</th>
                                        <th className="pb-2">Spot</th>
                                        <th className="pb-2">Futures</th>
                                        <th className="pb-2">Basis</th>
                                        <th className="pb-2">Funding</th>
                                        <th className="pb-2">APR Est.</th>
                                        <th className="pb-2"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {opportunities.map((opp, i) => (
                                        <tr key={i} className={`border-b border-white/5 ${opp.recommended ? 'bg-emerald-500/5' : ''}`}>
                                            <td className="py-3 font-bold text-white">{opp.symbol.replace('USDT', '')}</td>
                                            <td className="py-3 font-mono text-slate-300">${opp.spot_price.toLocaleString()}</td>
                                            <td className="py-3 font-mono text-slate-300">${opp.futures_price.toLocaleString()}</td>
                                            <td className={`py-3 font-mono ${opp.basis_percent > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                {opp.basis_percent > 0 ? '+' : ''}{opp.basis_percent.toFixed(3)}%
                                            </td>
                                            <td className="py-3 font-mono text-cyan-400">{(opp.funding_rate * 100).toFixed(4)}%</td>
                                            <td className="py-3 font-mono font-bold text-emerald-400">{opp.apr_estimate.toFixed(2)}%</td>
                                            <td className="py-3">
                                                {opp.recommended && (
                                                    <span className="text-[10px] px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400 font-bold uppercase">
                                                        Top
                                                    </span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Hedge Calculator */}
                <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                    <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <Calculator size={20} className="text-cyan-400" />
                        Calculadora de Hedge (Delta Neutral)
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label className="text-xs text-slate-500 uppercase font-bold mb-2 block">Posiciones Spot</label>
                            {Object.keys(spotHoldings).map(symbol => (
                                <div key={symbol} className="flex gap-2 mb-2">
                                    <input
                                        type="text"
                                        value={symbol}
                                        disabled
                                        className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                                    />
                                    <input
                                        type="number"
                                        step="0.0001"
                                        placeholder="Cantidad"
                                        value={spotHoldings[symbol]}
                                        onChange={(e) => setSpotHoldings({ ...spotHoldings, [symbol]: e.target.value })}
                                        className="w-32 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>

                    <button
                        onClick={calculateHedge}
                        className="px-6 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-bold hover:opacity-90 transition-all"
                    >
                        Calcular Hedge
                    </button>

                    {/* Results */}
                    {hedgeResults.length > 0 && (
                        <div className="mt-6 space-y-3">
                            {hedgeResults.map((result, i) => (
                                <div key={i} className={`p-4 rounded-lg border ${Math.abs(result.current_delta) < 0.0001
                                    ? 'bg-emerald-500/10 border-emerald-500/30'
                                    : 'bg-amber-500/10 border-amber-500/30'
                                    }`}>
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-bold text-white">{result.symbol.replace('USDT', '')}</span>
                                        {Math.abs(result.current_delta) < 0.0001 ? (
                                            <CheckCircle2 size={18} className="text-emerald-400" />
                                        ) : (
                                            <AlertCircle size={18} className="text-amber-400" />
                                        )}
                                    </div>
                                    <div className="text-sm space-y-1">
                                        <div className="flex justify-between text-slate-400">
                                            <span>Delta Actual:</span>
                                            <span className="text-white font-mono">{result.current_delta.toFixed(4)}</span>
                                        </div>
                                        <div className="flex justify-between text-slate-400">
                                            <span>Hedge Requerido:</span>
                                            <span className="text-white font-mono">{result.required_hedge.toFixed(4)}</span>
                                        </div>
                                        <p className="mt-2 text-xs text-slate-300">{result.recommendation}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </DashboardLayout>
    );
}
