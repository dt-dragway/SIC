'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import WhaleAlertWidget from '@/components/onchain/WhaleAlertWidget';
import {
    Monitor,
    TrendingUp,
    TrendingDown,
    Activity,
    BarChart3,
    ArrowUp,
    ArrowDown,
    Zap
} from 'lucide-react';

interface OrderBookItem {
    price: string;
    amount: string;
}

interface MarketDepth {
    symbol: string;
    bids: string[][]; // [price, amount]
    asks: string[][];
}

interface FundingData {
    symbol: string;
    fundingRate: number;
    markPrice: number;
    nextFundingTime: string;
}

export default function TerminalPage() {
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [depth, setDepth] = useState<MarketDepth | null>(null);
    const [funding, setFunding] = useState<FundingData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const token = localStorage.getItem('token');
                const headers = { 'Authorization': `Bearer ${token}` };

                const [depthRes, fundingRes] = await Promise.all([
                    fetch(`/api/v1/trading/depth/${symbol}?limit=15`, { headers }),
                    fetch(`/api/v1/trading/funding/${symbol}`, { headers })
                ]);

                if (depthRes.ok) setDepth(await depthRes.json());
                if (fundingRes.ok) setFunding(await fundingRes.json());

            } catch (error) {
                console.error("Error fetching terminal data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, [symbol]);

    // Calculate Spread
    const bestBid = depth?.bids[0] ? parseFloat(depth.bids[0][0]) : 0;
    const bestAsk = depth?.asks[0] ? parseFloat(depth.asks[0][0]) : 0;
    const spread = bestAsk - bestBid;
    const spreadPercent = bestBid > 0 ? (spread / bestBid) * 100 : 0;

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header & Symbol Select */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent flex items-center gap-3">
                            <Monitor className="text-blue-400" size={32} />
                            Terminal Pro Institucional
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">
                            Análisis de Microestructura y Flujo de Órdenes
                        </p>
                    </div>

                    <div className="flex gap-2">
                        {['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'].map(s => (
                            <button
                                key={s}
                                onClick={() => setSymbol(s)}
                                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all border ${symbol === s
                                    ? 'bg-blue-500/20 text-blue-400 border-blue-500/50'
                                    : 'bg-transparent text-slate-500 border-transparent hover:bg-white/5'}`}
                            >
                                {s.replace('USDT', '')}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Top Metrics Bar */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Mark Price */}
                    <div className="glass-card p-4 rounded-2xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex justify-between items-start">
                            <div>
                                <span className="text-[10px] uppercase font-bold text-slate-500">Precio Mark (Futuros)</span>
                                <p className="text-xl font-mono text-white font-bold mt-1">
                                    {funding?.markPrice ? `$${funding.markPrice.toLocaleString()}` : '---'}
                                </p>
                            </div>
                            <Activity size={18} className="text-slate-600" />
                        </div>
                    </div>

                    {/* Funding Rate */}
                    <div className="glass-card p-4 rounded-2xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex justify-between items-start">
                            <div>
                                <span className="text-[10px] uppercase font-bold text-slate-500">Tasa de Financiación</span>
                                <div className="flex items-center gap-2 mt-1">
                                    <p className={`text-xl font-mono font-bold ${(funding?.fundingRate || 0) > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {((funding?.fundingRate || 0) * 100).toFixed(4)}%
                                    </p>
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-slate-400">8h</span>
                                </div>
                            </div>
                            <Zap size={18} className={(funding?.fundingRate || 0) > 0.01 ? 'text-amber-400' : 'text-slate-600'} />
                        </div>
                    </div>

                    {/* Spread */}
                    <div className="glass-card p-4 rounded-2xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex justify-between items-start">
                            <div>
                                <span className="text-[10px] uppercase font-bold text-slate-500">Spread / Slippage Est.</span>
                                <p className="text-xl font-mono text-white font-bold mt-1">
                                    {spread.toFixed(2)} <span className="text-xs text-slate-500">({spreadPercent.toFixed(4)}%)</span>
                                </p>
                            </div>
                            <BarChart3 size={18} className="text-slate-600" />
                        </div>
                    </div>
                </div>

                {/* Main Content: Order Book & Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Order Book Column */}
                    <div className="glass-card rounded-3xl border border-white/5 bg-black/40 p-4 h-[600px] flex flex-col">
                        <h3 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
                            <BarChart3 size={16} /> Order Book (Profundidad)
                        </h3>

                        {/* Headers */}
                        <div className="grid grid-cols-3 text-[10px] font-bold text-slate-500 uppercase mb-2 px-2">
                            <span className="text-left">Precio</span>
                            <span className="text-right">Cantidad</span>
                            <span className="text-right">Total</span>
                        </div>

                        {/* Asks (Sells) - Red - Reversed */}
                        <div className="flex-1 overflow-hidden flex flex-col-reverse justify-end space-y-reverse space-y-[1px]">
                            {depth?.asks.slice(0, 15).reverse().map(([price, amount], i) => {
                                const total = parseFloat(price) * parseFloat(amount);
                                const width = Math.min((parseFloat(amount) / 5) * 100, 100); // Mock width calc
                                return (
                                    <div key={i} className="grid grid-cols-3 text-[11px] font-mono py-0.5 px-2 relative hover:bg-white/5">
                                        <div className="absolute top-0 right-0 bottom-0 bg-rose-500/10 z-0" style={{ width: `${width}%` }} />
                                        <span className="text-rose-400 z-10">{parseFloat(price).toFixed(2)}</span>
                                        <span className="text-slate-300 z-10 text-right">{parseFloat(amount).toFixed(4)}</span>
                                        <span className="text-slate-500 z-10 text-right">{total.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Spread Indicator */}
                        <div className="py-2 my-2 border-y border-white/5 text-center">
                            <span className={`text-base font-bold font-mono ${bestBid < bestAsk ? 'text-white' : 'text-amber-500'}`}>
                                {bestBid > 0 ? ((bestAsk + bestBid) / 2).toFixed(2) : '---'}
                            </span>
                        </div>

                        {/* Bids (Buys) - Green */}
                        <div className="flex-1 overflow-hidden space-y-[1px]">
                            {depth?.bids.map(([price, amount], i) => {
                                const total = parseFloat(price) * parseFloat(amount);
                                const width = Math.min((parseFloat(amount) / 5) * 100, 100);
                                return (
                                    <div key={i} className="grid grid-cols-3 text-[11px] font-mono py-0.5 px-2 relative hover:bg-white/5">
                                        <div className="absolute top-0 right-0 bottom-0 bg-emerald-500/10 z-0" style={{ width: `${width}%` }} />
                                        <span className="text-emerald-400 z-10">{parseFloat(price).toFixed(2)}</span>
                                        <span className="text-slate-300 z-10 text-right">{parseFloat(amount).toFixed(4)}</span>
                                        <span className="text-slate-500 z-10 text-right">{total.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Chart / Analysis Column (Placeholder for real charts/whale tracking) */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Microstructure Explained */}
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-indigo-500/10 to-purple-500/5">
                            <h3 className="text-lg font-bold text-indigo-300 mb-2">Microestructura de Mercado</h3>
                            <p className="text-slate-400 text-sm leading-relaxed">
                                El <strong>Order Book</strong> revela las intenciones reales de los participantes.
                                <br />
                                <span className="text-emerald-400">Muros de Compra (Bids)</span> soportan el precio, mientras que <span className="text-rose-400">Muros de Venta (Asks)</span> actúan como resistencia.
                                <br /><br />
                                <strong>Funding Rate:</strong> {funding?.fundingRate && funding.fundingRate > 0.01
                                    ? <span className="text-amber-400">Alto ({funding.fundingRate.toFixed(4)}%). Los Longs pagan a los Shorts. Posible corrección bajista (Long Squeeze).</span>
                                    : funding?.fundingRate && funding.fundingRate < 0
                                        ? <span className="text-emerald-400">Negativo ({funding.fundingRate.toFixed(4)}%). Los Shorts pagan a los Longs. Posible rebote alcista (Short Squeeze).</span>
                                        : <span className="text-slate-300">Neutral. Mercado equilibrado.</span>
                                }
                            </p>
                        </div>

                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-indigo-500/5 to-purple-500/5">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Activity size={20} className="text-cyan-400" />
                                Rastreo de Ballenas (Live Whale Alert)
                            </h3>
                            <WhaleAlertWidget blockchain={symbol.replace('USDT', '')} />
                        </div>
                    </div>

                </div>

            </div>
        </DashboardLayout>
    );
}
