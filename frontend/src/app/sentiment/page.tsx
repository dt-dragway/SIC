'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Newspaper, Zap, BarChart3, TrendingUp, Info, RefreshCw } from 'lucide-react';
import FearGreedMeter from '@/components/sentiment/FearGreedMeter';
import SentimentCard from '@/components/sentiment/SentimentCard';

interface NewsItem {
    id: number;
    title: string;
    source: string;
    sentiment: 'bullish' | 'bearish' | 'neutral';
    impact_score: number;
    time_ago: string;
}

interface SentimentData {
    symbol: string;
    overall_score: number;
    label: string;
    top_narrative: string;
    news: NewsItem[];
}

export default function SentimentPage() {
    const [data, setData] = useState<SentimentData | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchSentiment = async () => {
        setRefreshing(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/sentiment/market?symbol=BTCUSDT', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) setData(await res.json());
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchSentiment();
    }, []);

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="flex justify-between items-end">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-emerald-500 bg-clip-text text-transparent flex items-center gap-3">
                            <Newspaper size={32} className="text-cyan-400" />
                            AI Sentiment Hub
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">
                            Análisis de narrativas y flujo de noticias institucionales
                        </p>
                    </div>
                    <button
                        onClick={fetchSentiment}
                        disabled={refreshing}
                        className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-white transition-all"
                    >
                        <RefreshCw size={20} className={refreshing ? 'animate-spin' : ''} />
                    </button>
                </div>

                {loading ? (
                    <div className="h-[60vh] flex flex-col items-center justify-center">
                        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                        <p className="text-slate-500 font-medium">Escaneando prensa y redes sociales...</p>
                    </div>
                ) : data && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                        {/* Fear & Greed Section */}
                        <div className="lg:col-span-1 space-y-6">
                            <div className="glass-card p-8 rounded-3xl border border-white/5 bg-black/20 flex flex-col items-center justify-center">
                                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8 flex items-center gap-2">
                                    <Zap size={16} className="text-amber-400" />
                                    Market Sentiment Index
                                </h3>
                                <FearGreedMeter value={data.overall_score} label={data.label} />
                            </div>

                            <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-cyan-500/10 to-transparent">
                                <h4 className="text-xs font-bold text-cyan-400 uppercase mb-3">Narrativa Dominante</h4>
                                <p className="text-lg font-bold text-white leading-tight">
                                    "{data.top_narrative}"
                                </p>
                                <div className="mt-4 pt-4 border-t border-white/5 flex items-center gap-2 text-xs text-slate-500">
                                    <Info size={14} />
                                    <span>Analizado por el modelo Neural-Narrative v2</span>
                                </div>
                            </div>
                        </div>

                        {/* News Feed Section */}
                        <div className="lg:col-span-2">
                            <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                        <TrendingUp size={16} className="text-emerald-400" />
                                        Flujo de Noticias Críticas
                                    </h3>
                                    <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-slate-400 font-mono">
                                        Live Pulse
                                    </span>
                                </div>

                                <SentimentCard news={data.news} />

                                <div className="mt-6 p-4 rounded-xl border border-dashed border-white/10 flex items-center justify-center">
                                    <p className="text-xs text-slate-600 italic">
                                        En una implementación real, aquí verías noticias filtradas por impacto y relevancia algorítmica.
                                    </p>
                                </div>
                            </div>
                        </div>

                    </div>
                )}

                {/* Macro Correlation Info */}
                <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-r from-emerald-500/5 to-cyan-500/5 flex items-center gap-6">
                    <div className="p-4 rounded-2xl bg-cyan-500/10 text-cyan-400">
                        <BarChart3 size={24} />
                    </div>
                    <div>
                        <h4 className="font-bold text-white">Consejo del Agente IA</h4>
                        <p className="text-sm text-slate-400 leading-relaxed mt-1">
                            El sentimiento actual es <span className="text-cyan-400 font-bold">{data?.label}</span>.
                            Históricamente, los periodos de "Miedo" representan oportunidades de acumulación, mientras que la "Codicia Extrema" precede a correcciones. No ignores la divergencia entre precio y sentimiento.
                        </p>
                    </div>
                </div>

            </div>
        </DashboardLayout>
    );
}
