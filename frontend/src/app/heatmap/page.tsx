'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import {
    LayoutGrid,
    TrendingUp,
    TrendingDown,
    Filter,
    Activity,
    Layers,
    ArrowUpRight,
    Search
} from 'lucide-react';

interface HeatmapItem {
    symbol: string;
    sector: string;
    change_24h: number;
    volume_usd: number;
}

export default function HeatmapPage() {
    const [data, setData] = useState<HeatmapItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('All');

    const sectors = ['All', 'Layer 1', 'DeFi', 'AI & Data', 'Memes', 'L2'];

    useEffect(() => {
        fetchHeatmap();
    }, []);

    const fetchHeatmap = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/liquidity/heatmap', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) setData(await res.json());
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const filteredData = filter === 'All'
        ? data
        : data.filter(item => item.sector === filter);

    const getBgColor = (change: number) => {
        if (change > 5) return 'bg-emerald-500';
        if (change > 2) return 'bg-emerald-600/80';
        if (change > 0) return 'bg-emerald-900/40';
        if (change > -2) return 'bg-rose-900/40';
        if (change > -5) return 'bg-rose-600/80';
        return 'bg-rose-500';
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent flex items-center gap-3">
                            <LayoutGrid size={32} className="text-emerald-400" />
                            Market Heatmap
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">
                            Visualización de la fuerza relativa y flujos de capital por sector
                        </p>
                    </div>

                    <div className="flex items-center gap-2 bg-white/5 p-1 rounded-2xl border border-white/10">
                        {sectors.map(s => (
                            <button
                                key={s}
                                onClick={() => setFilter(s)}
                                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${filter === s ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'text-slate-500 hover:text-white'
                                    }`}
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                </div>

                {loading ? (
                    <div className="h-[60vh] flex flex-col items-center justify-center">
                        <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                        <p className="text-slate-500 font-medium">Calculando dominancia y flujos...</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                        {filteredData.map((item, i) => (
                            <div
                                key={i}
                                className={`group relative aspect-square p-4 rounded-2xl border border-white/5 flex flex-col justify-between transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer overflow-hidden ${getBgColor(item.change_24h)}`}
                            >
                                {/* Overlay for texture */}
                                <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-50"></div>

                                <div className="relative z-10 flex justify-between items-start">
                                    <span className="text-lg font-black tracking-tighter text-white">{item.symbol}</span>
                                    {item.change_24h > 0 ? <TrendingUp size={16} className="text-white/80" /> : <TrendingDown size={16} className="text-white/80" />}
                                </div>

                                <div className="relative z-10 flex flex-col">
                                    <span className="text-[10px] font-bold text-white/60 uppercase mb-0.5">{item.sector}</span>
                                    <span className="text-2xl font-bold text-white font-mono">
                                        {item.change_24h > 0 ? '+' : ''}{item.change_24h.toFixed(2)}%
                                    </span>
                                    <span className="text-[10px] text-white/40 mt-1">
                                        Vol: ${(item.volume_usd / 1_000_000).toFixed(1)}M
                                    </span>
                                </div>

                                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <ArrowUpRight size={14} className="text-white" />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Market Intelligence Tips */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20 flex items-start gap-4">
                        <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400">
                            <Activity size={20} />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-white mb-1">Rotación de Capital</h4>
                            <p className="text-[11px] text-slate-400 leading-relaxed">
                                Si ves que <span className="text-white font-bold">Memes</span> están excesivamente calientes (verde brillante) mientras <span className="text-white font-bold">Layer 1</span> están rojos, el mercado está en modo especulativo puro.
                            </p>
                        </div>
                    </div>

                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20 flex items-start gap-4">
                        <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400">
                            <Layers size={20} />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-white mb-1">Liderazgo de Sector</h4>
                            <p className="text-[11px] text-slate-400 leading-relaxed">
                                Los sectores que lideran la recuperación suelen ser los primeros en subir cuando BTC se estabiliza. Busca los bloques más grandes y verdes.
                            </p>
                        </div>
                    </div>

                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20 flex items-start gap-4">
                        <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-400">
                            <Search size={20} />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-white mb-1">Anomalías de Volumen</h4>
                            <p className="text-[11px] text-slate-400 leading-relaxed">
                                Un bloque rojo con volumen masivo puede indicar una capitulación institucional, a menudo una buena zona de compra de largo plazo.
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </DashboardLayout>
    );
}
