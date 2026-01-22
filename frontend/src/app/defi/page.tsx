'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Droplet, Shield, AlertCircle, TrendingDown } from 'lucide-react';

interface ILResult {
    impermanent_loss_percent: number;
    value_if_held: number;
    value_if_pooled: number;
    difference_usd: number;
    recommendation: string;
}

interface AuditResult {
    token_address: string;
    is_verified: boolean;
    red_flags: string[];
    risk_score: number;
    recommendation: string;
}

export default function DeFiPage() {
    // IL Calculator State
    const [initialTokenA, setInitialTokenA] = useState('');
    const [initialTokenB, setInitialTokenB] = useState('');
    const [initialRatio, setInitialRatio] = useState('');
    const [finalRatio, setFinalRatio] = useState('');
    const [ilResult, setIlResult] = useState<ILResult | null>(null);

    // Contract Auditor State
    const [tokenAddress, setTokenAddress] = useState('');
    const [blockchain, setBlockchain] = useState('ETH');
    const [auditResult, setAuditResult] = useState<AuditResult | null>(null);

    const calculateIL = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/defi/il-calculator', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    initial_token_a: parseFloat(initialTokenA),
                    initial_token_b: parseFloat(initialTokenB),
                    initial_price_ratio: parseFloat(initialRatio),
                    final_price_ratio: parseFloat(finalRatio)
                })
            });

            if (res.ok) setIlResult(await res.json());
        } catch (error) {
            console.error("Error calculating IL:", error);
        }
    };

    const auditContract = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/defi/contract-audit', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token_address: tokenAddress,
                    blockchain: blockchain
                })
            });

            if (res.ok) setAuditResult(await res.json());
        } catch (error) {
            console.error("Error auditing contract:", error);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-indigo-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Droplet size={32} className="text-purple-400" />
                        DeFi Advanced Tools
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Calculadora de IL y Auditor de Contratos
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Impermanent Loss Calculator */}
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingDown size={20} className="text-rose-400" />
                            Impermanent Loss Calculator
                        </h2>

                        <div className="space-y-3 mb-4">
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Token A Inicial</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={initialTokenA}
                                        onChange={(e) => setInitialTokenA(e.target.value)}
                                        placeholder="1.0"
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Token B Inicial</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={initialTokenB}
                                        onChange={(e) => setInitialTokenB(e.target.value)}
                                        placeholder="100.0"
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Ratio Inicial (B/A)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={initialRatio}
                                        onChange={(e) => setInitialRatio(e.target.value)}
                                        placeholder="100.0"
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Ratio Final (B/A)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={finalRatio}
                                        onChange={(e) => setFinalRatio(e.target.value)}
                                        placeholder="200.0"
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={calculateIL}
                            className="w-full px-6 py-2 rounded-lg bg-gradient-to-r from-rose-500 to-pink-500 text-white font-bold hover:opacity-90 transition-all mb-4"
                        >
                            Calcular IL
                        </button>

                        {ilResult && (
                            <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Impermanent Loss:</span>
                                    <span className="text-rose-400 font-mono font-bold">{ilResult.impermanent_loss_percent.toFixed(2)}%</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Valor si HODL:</span>
                                    <span className="text-white font-mono">${ilResult.value_if_held.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Valor en Pool:</span>
                                    <span className="text-white font-mono">${ilResult.value_if_pooled.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-sm font-bold">
                                    <span className="text-slate-300">Diferencia:</span>
                                    <span className={ilResult.difference_usd < 0 ? 'text-rose-400' : 'text-emerald-400'}>
                                        ${ilResult.difference_usd.toFixed(2)}
                                    </span>
                                </div>
                                <p className="text-xs text-slate-300 mt-3 pt-3 border-t border-white/10">{ilResult.recommendation}</p>
                            </div>
                        )}
                    </div>

                    {/* Contract Auditor */}
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Shield size={20} className="text-cyan-400" />
                            Contract Auditor (Red Flags)
                        </h2>

                        <div className="space-y-3 mb-4">
                            <div>
                                <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Blockchain</label>
                                <select
                                    value={blockchain}
                                    onChange={(e) => setBlockchain(e.target.value)}
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                                >
                                    <option value="ETH">Ethereum</option>
                                    <option value="BSC">BSC</option>
                                    <option value="POLYGON">Polygon</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Token Address</label>
                                <input
                                    type="text"
                                    value={tokenAddress}
                                    onChange={(e) => setTokenAddress(e.target.value)}
                                    placeholder="0x..."
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono"
                                />
                            </div>
                        </div>

                        <button
                            onClick={auditContract}
                            className="w-full px-6 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold hover:opacity-90 transition-all mb-4"
                        >
                            Auditar Contrato
                        </button>

                        {auditResult && (
                            <div className={`p-4 rounded-lg border ${auditResult.risk_score > 50
                                    ? 'bg-rose-500/10 border-rose-500/30'
                                    : 'bg-emerald-500/10 border-emerald-500/30'
                                } space-y-3`}>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-slate-400">Risk Score:</span>
                                    <span className={`text-lg font-bold font-mono ${auditResult.risk_score > 50 ? 'text-rose-400' : 'text-emerald-400'
                                        }`}>
                                        {auditResult.risk_score}/100
                                    </span>
                                </div>

                                <div className="space-y-1">
                                    {auditResult.red_flags.map((flag, i) => (
                                        <div key={i} className="flex items-start gap-2 text-xs">
                                            <AlertCircle size={12} className="mt-0.5 text-amber-400" />
                                            <span className="text-slate-300">{flag}</span>
                                        </div>
                                    ))}
                                </div>

                                <p className="text-xs text-slate-300 mt-3 pt-3 border-t border-white/10">
                                    {auditResult.recommendation}
                                </p>
                            </div>
                        )}
                    </div>

                </div>

            </div>
        </DashboardLayout>
    );
}
